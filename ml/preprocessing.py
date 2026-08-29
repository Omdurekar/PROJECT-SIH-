from typing import Tuple, Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from ml.feature_engineering import engineer_features, FEATURE_COLUMNS

TARGET_MAPPING = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
REVERSE_TARGET_MAPPING = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

class MLPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = FEATURE_COLUMNS

    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        # 1. Feature Engineering
        df_engineered = engineer_features(df)

        # 2. Extract Features
        X = df_engineered[self.feature_columns].fillna(0.0)

        # 3. Fit & Transform Scaler
        X_scaled = self.scaler.fit_transform(X)

        # 4. Target Encoding
        y_labels = df["delay_level"].map(TARGET_MAPPING).values

        return X_scaled, y_labels

    def transform_single(self, input_dict: Dict[str, Any]) -> np.ndarray:
        """
        Transforms a single project dictionary for inference.
        """
        df_single = pd.DataFrame([input_dict])
        df_engineered = engineer_features(df_single)
        X_single = df_engineered[self.feature_columns].fillna(0.0)
        X_scaled = self.scaler.transform(X_single)
        return X_scaled
