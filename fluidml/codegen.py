"""HLS code generation support."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from jinja2 import Environment, FileSystemLoader

from .config import FluidMLConfig
from .data import DataManager

logger = logging.getLogger(__name__)


def _resolve_template_dir() -> Path:
    """Find template directory in packaged or source-checkout layouts."""
    candidates = [
        Path(__file__).resolve().parent / "templates",
        Path(__file__).resolve().parent.parent / "templates",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Template directory not found. Expected one of: "
        + ", ".join(str(path) for path in candidates)
    )


class CodeGenerator(ABC):
    """Abstract base class for code generators."""

    def __init__(self, config: FluidMLConfig):
        self.config = config
        self.output_dir = Path(config.config["project"]["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate_headers(self, model: Any, data_manager: DataManager) -> List[str]:
        pass

    @abstractmethod
    def generate_implementation(self, model: Any, data_manager: DataManager) -> List[str]:
        pass

    @abstractmethod
    def generate_x_test_header(self, x_test: np.ndarray) -> str:
        pass

    @abstractmethod
    def generate_rfr_tb(self, target_cols: List[str]) -> str:
        pass


class Jinja2HLSCodeGenerator(CodeGenerator):
    """Jinja2-based HLS code generator."""

    def __init__(self, config: FluidMLConfig):
        super().__init__(config)
        template_dir = _resolve_template_dir()
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        self.precision_type = self._get_precision_type()
        self.backend = config.backend

    def _get_precision_type(self) -> str:
        precision = self.config.config["export"]["precision"]
        if precision == "float":
            return "float"
        if precision == "fixed":
            return "ap_fixed<16,6>"
        if precision.startswith("ap_fixed"):
            return precision
        return "float"

    def _extract_tree_data(self, tree_obj: Any, max_nodes: int) -> dict:
        tree_data = tree_obj.tree_
        n_nodes = tree_data.node_count

        features_array = tree_data.feature
        thresholds_array = tree_data.threshold
        values_array = tree_data.value.flatten()
        left_array = tree_data.children_left
        right_array = tree_data.children_right

        features = np.where(features_array >= 0, features_array, 0).astype(np.int32)
        thresholds = np.where(thresholds_array != -2, thresholds_array, 0.0).astype(np.float64)
        values = values_array.astype(np.float64)
        left = np.where(left_array >= 0, left_array, 0).astype(np.int32)
        right = np.where(right_array >= 0, right_array, 0).astype(np.int32)
        is_leaf = (tree_data.children_left == -1).astype(np.int32)

        pad_size = max_nodes - n_nodes
        if pad_size > 0:
            features = np.pad(features, (0, pad_size), constant_values=0)
            thresholds = np.pad(thresholds, (0, pad_size), constant_values=0.0)
            values = np.pad(values, (0, pad_size), constant_values=0.0)
            left = np.pad(left, (0, pad_size), constant_values=0)
            right = np.pad(right, (0, pad_size), constant_values=0)
            is_leaf = np.pad(is_leaf, (0, pad_size), constant_values=0)

        result = {
            "features": [int(features[index]) for index in range(len(features))],
            "thresholds": [float(thresholds[index]) for index in range(len(thresholds))],
            "node_values": [float(values[index]) for index in range(len(values))],
            "left_children": [int(left[index]) for index in range(len(left))],
            "right_children": [int(right[index]) for index in range(len(right))],
            "is_leaf": [int(is_leaf[index]) for index in range(len(is_leaf))],
            "n_nodes": int(n_nodes),
        }
        return result

    def _build_context(self, data_manager: DataManager, model: Any = None) -> dict:
        n_features = len(data_manager.feature_cols)
        n_targets = len(data_manager.target_cols)
        max_nodes = self.config.config["export"]["max_nodes"]

        context = {
            "n_features": n_features,
            "n_targets": n_targets,
            "n_trees": self.config.config["model"]["n_estimators"],
            "max_depth": self.config.config["model"]["max_depth"],
            "max_nodes": max_nodes,
            "precision_type": self.precision_type,
            "precision": self.config.config["export"]["precision"],
            "feature_cols": list(data_manager.feature_cols),
            "target_cols": list(data_manager.target_cols),
            "backend": self.backend.backend,
            "is_vitis": self.backend.is_vitis(),
            "backend_macro": self.backend.get_define_macro(),
            "requires_const_rom": self.backend.config["requires_const_rom"],
        }

        if model is not None:
            if n_targets > 1:
                estimators_list = model.estimators_
            else:
                estimators_list = [model]

            n_trees_per_target = len(estimators_list[0].estimators_)
            tree_data = []
            for forest in estimators_list:
                target_trees = []
                for tree in forest.estimators_:
                    tree_dict = self._extract_tree_data(tree, max_nodes)
                    target_trees.append(tree_dict)
                tree_data.append(target_trees)

            target_trees_list = []
            for target_idx in range(len(estimators_list)):
                trees = [f"target{target_idx}_tree{index}" for index in range(n_trees_per_target)]
                target_trees_list.append(trees)

            context.update(
                {
                    "n_trees_per_target": n_trees_per_target,
                    "tree_data": tree_data,
                    "target_trees_list": target_trees_list,
                }
            )

        if data_manager.scaler_x:
            context["scaler_x"] = True
            context["scaler_x_data_min"] = [float(value) for value in data_manager.scaler_x.data_min_]
            context["scaler_x_data_range"] = [float(value) for value in data_manager.scaler_x.data_range_]

        if data_manager.scaler_y:
            context["scaler_y"] = True
            context["scaler_y_data_min"] = [float(value) for value in data_manager.scaler_y.data_min_]
            context["scaler_y_data_range"] = [float(value) for value in data_manager.scaler_y.data_range_]

        return context

    def generate_headers(self, model: Any, data_manager: DataManager) -> List[str]:
        generated_files: List[str] = []
        context = self._build_context(data_manager, model)
        headers = [
            ("firmware/rfr_common.h.j2", "rfr_common.h"),
            ("firmware/rf_trees_array.h.j2", "rf_trees_array.h"),
            ("firmware/bitcast_utils.h.j2", "bitcast_utils.h"),
            ("firmware/scaler_constants.h.j2", "scaler_constants.h"),
        ]

        for template_name, output_name in headers:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            output_path = self.output_dir / output_name
            output_path.write_text(content, encoding="utf-8")
            generated_files.append(str(output_path))
            logger.info("Generated %s/%s", self.output_dir.name, output_name)
        return generated_files

    def generate_implementation(self, model: Any, data_manager: DataManager) -> List[str]:
        generated_files: List[str] = []
        context = self._build_context(data_manager, model)
        context.update(
            {
                "n_targets": len(data_manager.target_cols),
                "n_trees": self.config.config["model"]["n_estimators"],
            }
        )
        implementations = [
            ("firmware/myproj_axi.cpp.j2", "myproj_axi.cpp"),
            ("firmware/myproj_core.cpp.j2", "myproj_core.cpp"),
            ("firmware/model_predict.cpp.j2", "model_predict.cpp"),
        ]

        for template_name, output_name in implementations:
            template = self.env.get_template(template_name)
            content = template.render(**context)
            output_path = self.output_dir / output_name
            output_path.write_text(content, encoding="utf-8")
            generated_files.append(str(output_path))
            logger.info("Generated %s/%s", self.output_dir.name, output_name)
        return generated_files

    def generate_x_test_header(self, x_test: np.ndarray) -> str:
        x_test_data = [[float(value) for value in row] for row in x_test]
        context = {
            "x_test_samples": len(x_test),
            "x_test_data": x_test_data,
        }
        template = self.env.get_template("test/X_test.h.j2")
        content = template.render(**context)
        path = self.output_dir / "X_test.h"
        path.write_text(content, encoding="utf-8")
        logger.info("Generated %s/X_test.h", self.output_dir.name)
        return str(path)

    def generate_rfr_tb(self, target_cols: List[str]) -> str:
        context = {
            "target_names": list(target_cols),
            "csv_header": ",".join(target_cols),
            "n_targets": len(target_cols),
        }
        template = self.env.get_template("test/rfr_tb.cpp.j2")
        content = template.render(**context)
        path = self.output_dir / "rfr_tb.cpp"
        path.write_text(content, encoding="utf-8")
        logger.info("Generated %s/rfr_tb.cpp", self.output_dir.name)
        return str(path)
