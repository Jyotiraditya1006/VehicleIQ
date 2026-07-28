"""
VehicleIQ Driving Style Classifier Module
Uses Scikit-Learn (Random Forest) to categorize driver behavior into gentle, moderate, or aggressive styles.
"""

import os
import logging
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger("VehicleIQ.DrivingStyleClassifier")

FEATURE_COLUMNS = [
    "hard_braking_rate",
    "hard_accel_rate",
    "high_rpm_ratio",
    "extreme_rpm_ratio",
    "idle_ratio",
    "speed_mean",
    "speed_std",
    "throttle_mean",
    "throttle_std",
]

CLASSES = ["gentle", "moderate", "aggressive"]

class DrivingStyleClassifier:
    """Classifies sliding window behavior features into driving style categories."""

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

    @staticmethod
    def generate_heuristic_labels(df_features: pd.DataFrame) -> pd.Series:
        """Generates ground-truth labels based on physical behavioral thresholds."""
        labels = []
        for _, row in df_features.iterrows():
            if (
                row.get("hard_braking_rate", 0) > 0.08
                or row.get("hard_accel_rate", 0) > 0.08
                or row.get("high_rpm_ratio", 0) > 0.15
                or row.get("extreme_rpm_ratio", 0) > 0.05
                or row.get("throttle_std", 0) > 22.0
            ):
                labels.append("aggressive")
            elif (
                row.get("high_rpm_ratio", 0) == 0
                and row.get("hard_braking_rate", 0) == 0
                and row.get("speed_std", 0) < 12.0
            ):
                labels.append("gentle")
            else:
                labels.append("moderate")
        return pd.Series(labels)

    def train(self, df_features: pd.DataFrame, labels: pd.Series) -> Dict[str, float]:
        """Trains the Random Forest classifier on extracted features."""
        X = df_features[FEATURE_COLUMNS].copy()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        self.model.fit(X_scaled, labels)
        self.is_trained = True
        
        accuracy = float(self.model.score(X_scaled, labels))
        logger.info(f"Driving Style Classifier trained successfully with Accuracy: {accuracy:.4f}")
        return {"accuracy": accuracy}

    def predict(self, feature_dict: Dict[str, float]) -> Dict[str, Any]:
        """
        Predicts driving style for a single window feature dictionary.
        Returns predicted label, confidence probabilities, and driving behavior score (0-100).
        """
        if not self.is_trained:
            # Fallback heuristic prediction if model file not yet trained
            heuristic_label = self.generate_heuristic_labels(pd.DataFrame([feature_dict])).iloc[0]
            scores = {"gentle": 85.0, "moderate": 60.0, "aggressive": 25.0}
            return {
                "predicted_style": heuristic_label,
                "confidence": 0.85,
                "probabilities": {"gentle": 0.33, "moderate": 0.33, "aggressive": 0.33},
                "driving_behavior_score": scores[heuristic_label],
            }

        X_input = pd.DataFrame([feature_dict])[FEATURE_COLUMNS]
        X_scaled = self.scaler.transform(X_input)
        
        pred_label = str(self.model.predict(X_scaled)[0])
        probas = self.model.predict_proba(X_scaled)[0]
        
        prob_dict = {cls_name: float(prob) for cls_name, prob in zip(self.model.classes_, probas)}
        confidence = float(prob_dict.get(pred_label, 0.0))

        # Calculate a continuous 0-100 driving behavior score
        # Higher score = gentler, safer driving
        score = 100.0 * (prob_dict.get("gentle", 0.0) * 1.0 + prob_dict.get("moderate", 0.0) * 0.65 + prob_dict.get("aggressive", 0.0) * 0.20)
        score = round(max(0.0, min(100.0, score)), 1)

        return {
            "predicted_style": pred_label,
            "confidence": round(confidence, 3),
            "probabilities": prob_dict,
            "driving_behavior_score": score,
        }

    def save(self, filepath: str = "models/driving_style_model.joblib"):
        """Saves model and scaler to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"model": self.model, "scaler": self.scaler, "is_trained": self.is_trained}, filepath)
        logger.info(f"Saved Driving Style Classifier to {filepath}")

    def load(self, filepath: str = "models/driving_style_model.joblib") -> bool:
        """Loads trained model and scaler from disk."""
        if not os.path.exists(filepath):
            logger.warning(f"Model file not found at {filepath}")
            return False
        data = joblib.load(filepath)
        self.model = data["model"]
        self.scaler = data["scaler"]
        self.is_trained = data["is_trained"]
        logger.info(f"Loaded Driving Style Classifier from {filepath}")
        return True
