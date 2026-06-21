"""HLS code generation support."""

from __future__ import annotations

import logging
import math
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from jinja2 import Environment, FileSystemLoader

from .config import CambiumConfig
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

    def __init__(self, config: CambiumConfig):
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

    def __init__(self, config: CambiumConfig):
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

    @staticmethod
    def _parse_ap_fixed_type(precision_type: str) -> tuple[int, int]:
        match = re.fullmatch(r"ap_fixed\s*<\s*(\d+)\s*,\s*(\d+)(?:\s*,.*)?\s*>", precision_type)
        if not match:
            raise ValueError(f"Unsupported precision format: {precision_type}")

        total_bits = int(match.group(1))
        int_bits = int(match.group(2))

        if total_bits > 32:
            raise ValueError(
                f"Precision {precision_type} exceeds the 32-bit AXI stream payload supported by this framework."
            )
        if int_bits > total_bits:
            raise ValueError(f"Invalid precision {precision_type}: integer bits exceed total bits.")

        return total_bits, int_bits

    def _build_precision_context(self, n_trees_per_target: int) -> Dict[str, Any]:
        if self.precision_type == "float":
            return {
                "feature_total_bits": 32,
                "score_total_bits": 32,
                "accum_precision_type": "float",
            }

        total_bits, int_bits = self._parse_ap_fixed_type(self.precision_type)
        required_accum_int_bits = self._bits_for_max_value(max(1, n_trees_per_target)) + 1
        accum_int_bits = max(int_bits, required_accum_int_bits)
        accum_total_bits = total_bits + max(0, accum_int_bits - int_bits)

        return {
            "feature_total_bits": total_bits,
            "score_total_bits": total_bits,
            "accum_precision_type": f"ap_fixed<{accum_total_bits},{accum_int_bits}>",
        }

    def _extract_tree_data(self, tree_obj: Any, max_nodes: int, task: str, output_dim: int) -> dict:
        tree_data = tree_obj.tree_
        n_nodes = tree_data.node_count

        features_array = tree_data.feature
        thresholds_array = tree_data.threshold
        left_array = tree_data.children_left
        right_array = tree_data.children_right

        features = np.where(features_array >= 0, features_array, 0).astype(np.int32)
        thresholds = np.where(thresholds_array != -2, thresholds_array, 0.0).astype(np.float64)
        left = np.where(left_array >= 0, left_array, 0).astype(np.int32)
        right = np.where(right_array >= 0, right_array, 0).astype(np.int32)
        is_leaf = (tree_data.children_left == -1).astype(np.int32)

        if task == "classification":
            values = tree_data.value[:, 0, :output_dim].astype(np.float64)
            denom = values.sum(axis=1, keepdims=True)
            values = np.divide(values, denom, out=np.zeros_like(values), where=denom != 0)
        else:
            values = tree_data.value.flatten().astype(np.float64)

        pad_size = max_nodes - n_nodes
        if pad_size > 0:
            features = np.pad(features, (0, pad_size), constant_values=0)
            thresholds = np.pad(thresholds, (0, pad_size), constant_values=0.0)
            left = np.pad(left, (0, pad_size), constant_values=0)
            right = np.pad(right, (0, pad_size), constant_values=0)
            is_leaf = np.pad(is_leaf, (0, pad_size), constant_values=0)
            if task == "classification":
                values = np.pad(values, ((0, pad_size), (0, 0)), constant_values=0.0)
            else:
                values = np.pad(values, (0, pad_size), constant_values=0.0)

        result = {
            "features": [int(features[index]) for index in range(len(features))],
            "thresholds": [float(thresholds[index]) for index in range(len(thresholds))],
            "left_children": [int(left[index]) for index in range(len(left))],
            "right_children": [int(right[index]) for index in range(len(right))],
            "is_leaf": [int(is_leaf[index]) for index in range(len(is_leaf))],
            "n_nodes": int(n_nodes),
        }
        if task == "classification":
            result["node_values"] = [
                [float(values[node_idx, class_idx]) for class_idx in range(output_dim)]
                for node_idx in range(values.shape[0])
            ]
        else:
            result["node_values"] = [float(values[index]) for index in range(len(values))]
        return result

    def _get_forest_estimators(self, model: Any, task: str, output_dim: int) -> List[List[Any]]:
        if task == "classification":
            return [list(model.estimators_)]
        if output_dim > 1:
            return [list(forest.estimators_) for forest in model.estimators_]
        return [list(model.estimators_)]

    def _get_model_max_nodes(self, model: Any, task: str, output_dim: int) -> int:
        max_nodes = 0
        for forest in self._get_forest_estimators(model, task, output_dim):
            for tree in forest:
                max_nodes = max(max_nodes, int(tree.tree_.node_count))
        return max_nodes

    @staticmethod
    def _bits_for_max_value(max_value: int) -> int:
        """Minimum unsigned bit width needed to represent [0, max_value]."""
        return max(1, int(math.ceil(math.log2(max(2, max_value + 1)))))

    def _build_context(self, data_manager: DataManager, model: Any = None) -> dict:
        task = self.config.config["model"]["task"]
        is_classification = task == "classification"
        n_features = len(data_manager.feature_cols)
        n_targets = len(data_manager.target_cols)
        output_dim = n_targets
        output_names = list(data_manager.target_cols)
        forest_names = list(data_manager.target_cols)
        n_forests = n_targets
        configured_max_nodes = int(self.config.config["export"].get("max_nodes", 128))
        model_max_nodes = 0
        n_trees_per_target = int(self.config.config["model"]["n_estimators"])

        if is_classification:
            if n_targets != 1:
                raise NotImplementedError("Classification export currently supports exactly one target column.")
            if model is None or not hasattr(model, "classes_"):
                raise ValueError("Classification export requires a trained classifier with classes_.")
            output_names = [f"class_{cls}" for cls in model.classes_]
            output_dim = len(output_names)
            n_forests = 1

        if model is not None:
            model_max_nodes = self._get_model_max_nodes(model, task, output_dim)

        max_nodes = max(configured_max_nodes, model_max_nodes)
        feature_index_bits = self._bits_for_max_value(max(0, n_features - 1))
        node_index_bits = self._bits_for_max_value(max_nodes)

        context = {
            "n_features": n_features,
            "n_targets": output_dim,
            "n_forests": n_forests,
            "n_trees": self.config.config["model"]["n_estimators"],
            "max_depth": self.config.config["model"]["max_depth"],
            "max_nodes": max_nodes,
            "feature_index_bits": feature_index_bits,
            "node_index_bits": node_index_bits,
            "precision_type": self.precision_type,
            "precision": self.config.config["export"]["precision"],
            "feature_cols": list(data_manager.feature_cols),
            "target_cols": list(data_manager.target_cols),
            "output_names": output_names,
            "forest_names": forest_names,
            "task": task,
            "is_classification": is_classification,
            "is_regression": not is_classification,
            "backend": self.backend.backend,
            "is_vitis": self.backend.is_vitis(),
            "backend_macro": self.backend.get_define_macro(),
            "requires_const_rom": self.backend.config["requires_const_rom"],
        }
        context.update(self._build_precision_context(n_trees_per_target))

        if model is not None:
            forest_estimators = self._get_forest_estimators(model, task, output_dim)

            if model_max_nodes > configured_max_nodes:
                logger.warning(
                    "Model requires %s nodes per tree, increasing MAX_NNODES from %s to %s.",
                    model_max_nodes,
                    configured_max_nodes,
                    max_nodes,
                )

            tree_data = []
            for forest in forest_estimators:
                target_trees = []
                for tree in forest:
                    tree_dict = self._extract_tree_data(tree, max_nodes, task, output_dim)
                    target_trees.append(tree_dict)
                tree_data.append(target_trees)

            target_trees_list = []
            for target_idx in range(len(forest_estimators)):
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

    def generate_rfr_tb(self, output_names: List[str], task: str) -> str:
        context = {
            "target_names": [str(name) for name in output_names],
            "csv_header": ",".join(str(name) for name in output_names),
            "n_targets": len(output_names),
            "is_classification": task == "classification",
            "is_regression": task != "classification",
        }
        template = self.env.get_template("test/rfr_tb.cpp.j2")
        content = template.render(**context)
        path = self.output_dir / "rfr_tb.cpp"
        path.write_text(content, encoding="utf-8")
        logger.info("Generated %s/rfr_tb.cpp", self.output_dir.name)
        return str(path)
