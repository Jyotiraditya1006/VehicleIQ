"""
VehicleIQ Phase 2 Verification Test Suite
Automated verification tests for feature engineering, ML models, and plain-language explainability.
"""

import os
import unittest
import pandas as pd
import numpy as np

from obd_simulator import OBDSimulator
from feature_engineering import OBDFeatureExtractor
from driving_style_classifier import DrivingStyleClassifier
from degradation_lstm_model import ComponentHealthPredictor
from explainability import ExplainabilityEngine

class TestPhase2MLPipeline(unittest.TestCase):

    def test_01_feature_engineering(self):
        """Verify feature extractor computes rolling metrics from telemetry."""
        sim = OBDSimulator(vehicle_id="TEST_FEAT", scenario="aggressive_sport")
        raw_samples = [sim.generate_sample() for _ in range(40)]
        df_raw = pd.DataFrame(raw_samples)
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])

        extractor = OBDFeatureExtractor(window_size=30)
        df_features = extractor.transform_dataframe(df_raw, step_size=5)

        self.assertFalse(df_features.empty)
        self.assertIn("hard_braking_rate", df_features.columns)
        self.assertIn("high_rpm_ratio", df_features.columns)
        self.assertIn("thermal_stress_index", df_features.columns)

    def test_02_driving_style_classifier(self):
        """Verify driving style classification and behavior score calculation."""
        sim = OBDSimulator(vehicle_id="TEST_CLS", scenario="aggressive_sport")
        raw_samples = [sim.generate_sample() for _ in range(35)]
        df_raw = pd.DataFrame(raw_samples)
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])

        extractor = OBDFeatureExtractor(window_size=30)
        feat_df = extractor.transform_dataframe(df_raw)
        feat_dict = feat_df.iloc[0].to_dict()

        classifier = DrivingStyleClassifier()
        # Train on heuristic labels
        labels = classifier.generate_heuristic_labels(feat_df)
        classifier.train(feat_df, labels)

        res = classifier.predict(feat_dict)
        self.assertIn("predicted_style", res)
        self.assertIn("driving_behavior_score", res)
        self.assertGreaterEqual(res["driving_behavior_score"], 0.0)
        self.assertLessEqual(res["driving_behavior_score"], 100.0)

    def test_03_component_health_predictor(self):
        """Verify LSTM / Physics component health degradation model."""
        sim = OBDSimulator(vehicle_id="TEST_HEALTH", scenario="thermal_overheat")
        raw_samples = [sim.generate_sample() for _ in range(45)]
        df_raw = pd.DataFrame(raw_samples)
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])

        extractor = OBDFeatureExtractor(window_size=30)
        feat_df = extractor.transform_dataframe(df_raw, step_size=2)

        predictor = ComponentHealthPredictor(sequence_length=5)
        res = predictor.predict_sequence(feat_df)

        self.assertIn("brake_health", res)
        self.assertIn("engine_health", res)
        self.assertIn("battery_health", res)

        # Ensure health percentages are bounded between 0 and 100
        for comp in ["brake_health", "engine_health", "battery_health"]:
            self.assertGreaterEqual(res[comp], 0.0)
            self.assertLessEqual(res[comp], 100.0)

    def test_04_explainability_plain_language(self):
        """Verify plain-language diagnostic alert generation."""
        engine = ExplainabilityEngine()
        
        mock_features = {
            "hard_braking_rate": 0.12,
            "coolant_temp_max": 105.5,
            "high_rpm_ratio": 0.25,
            "battery_voltage_min": 11.8,
            "battery_voltage_std": 0.45,
            "thermal_stress_index": 3.5,
        }
        
        mock_style = {
            "predicted_style": "aggressive",
            "driving_behavior_score": 35.0
        }
        
        mock_health = {
            "brake_health": 62.0,
            "engine_health": 58.0,
            "battery_health": 64.0
        }

        report = engine.generate_full_report("VEHICLE_ALERT_TEST", mock_features, mock_style, mock_health)
        
        self.assertIn("vehicle_id", report)
        self.assertIn("plain_language_alerts", report)
        self.assertGreater(len(report["plain_language_alerts"]), 0)
        
        # Verify plain-English text components exist
        alert_components = [a["component"] for a in report["plain_language_alerts"]]
        self.assertIn("Brakes", alert_components)
        self.assertIn("Engine", alert_components)
        self.assertIn("Battery", alert_components)
        
        # Verify readable explanation string contains human-friendly numbers and recommendations
        for alert in report["plain_language_alerts"]:
            self.assertIsNotNone(alert.get("explanation"))
            self.assertIsNotNone(alert.get("recommendation"))

if __name__ == "__main__":
    unittest.main()
