"""Data loading and preprocessing utilities."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

from .config import FluidMLConfig

logger = logging.getLogger(__name__)


class DataManager:
    """Handles data loading, preprocessing, and scaling."""

    def __init__(self, config: FluidMLConfig):
        self.config = config
        self.scaler_x = None
        self.scaler_y = None
        self.data = None
        self.feature_cols: Optional[List[str]] = None
        self.target_cols: Optional[List[str]] = None
        self.data_source = None

    def load_data(
        self,
        data_source: Union[str, pd.DataFrame],
        feature_cols: Optional[List[str]] = None,
        target_cols: Optional[List[str]] = None,
    ) -> Tuple[pd.DataFrame, List[str], List[str]]:
        try:
            self.data_source = data_source
            if isinstance(data_source, str):
                self.data = pd.read_csv(data_source)
            else:
                self.data = data_source

            self.feature_cols = feature_cols or self.config.config["data"]["feature_cols"]
            self.target_cols = target_cols or self.config.config["data"]["target_cols"]

            if not self.feature_cols or not self.target_cols:
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
                if not numeric_cols:
                    raise ValueError("Dataset does not contain numeric columns for auto-selection")
                if not self.target_cols:
                    self.target_cols = [numeric_cols[-1]]
                if not self.feature_cols:
                    self.feature_cols = numeric_cols[: -len(self.target_cols)]

            missing_cols = set(self.feature_cols + self.target_cols) - set(self.data.columns)
            if missing_cols:
                raise ValueError(f"Missing columns: {sorted(missing_cols)}")

            self.config.config["data"]["source"] = str(data_source)
            self.config.config["data"]["feature_cols"] = list(self.feature_cols)
            self.config.config["data"]["target_cols"] = list(self.target_cols)

            logger.info("Dataset loaded successfully. Shape: %s", self.data.shape)
            logger.info("Features: %s", self.feature_cols)
            logger.info("Targets: %s", self.target_cols)
            return self.data, self.feature_cols, self.target_cols
        except Exception as exc:
            logger.error("Error loading data: %s", exc)
            raise

    def prepare_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        if self.data is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        x_data = self.data[self.feature_cols].values
        y_data = self.data[self.target_cols].values

        if len(x_data) == 0 or len(y_data) == 0:
            raise ValueError("No data available after loading")

        if np.any(np.isnan(x_data)) or np.any(np.isnan(y_data)):
            logger.warning("Data contains NaN values, filling with zeros")
            x_data = np.nan_to_num(x_data)
            y_data = np.nan_to_num(y_data)

        x_train, x_test, y_train, y_test = train_test_split(
            x_data,
            y_data,
            test_size=self.config.config["data"]["test_size"],
            random_state=self.config.config["model"]["random_state"],
        )

        if len(x_test) == 0:
            logger.warning("No test data after split, using a small portion of training data")
            x_test = x_train[:10]
            y_test = y_train[:10]
            x_train = x_train[10:]
            y_train = y_train[10:]

        scaler_type = self.config.config["data"]["scaler"]
        if scaler_type == "minmax":
            self.scaler_x = MinMaxScaler()
        elif scaler_type == "standard":
            self.scaler_x = StandardScaler()
        elif scaler_type == "robust":
            self.scaler_x = RobustScaler()
        else:
            self.scaler_x = None

        if self.scaler_x:
            x_train = self.scaler_x.fit_transform(x_train)
            x_test = self.scaler_x.transform(x_test)

        if self.config.config["model"]["task"] == "regression":
            self.scaler_y = MinMaxScaler()
            y_train = self.scaler_y.fit_transform(y_train)
            y_test = self.scaler_y.transform(y_test)

        logger.info("Data prepared - Train: %s, Test: %s", x_train.shape, x_test.shape)
        return x_train, x_test, y_train, y_test
