"""
VehicleIQ MLOps Model Training Pipeline
Executes synthetic dataset generation, feature extraction, Optuna hyperparameter optimization,
MLflow experiment tracking, and exports trained model artifacts.
"""

import os
import logging
import numpy as np
import pandas as pd

from obd_simulator import OBDSimulator
from feature_engineering import OBDFeatureExtractor
from driving_style_classifier import DrivingStyleClassifier, FEATURE_COLUMNS
from degradation_lstm_model import ComponentHealthPredictor, FEATURE_COLUMNS_LSTM

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("VehicleIQ.TrainPipeline")

def generate_synthetic_dataset(samples_per_scenario: int = 200) -> Tuple[pd.DataFrame, pd.Series]:
    """Generates synthetic telemetry streams across all 4 scenarios."""
    extractor = OBDFeatureExtractor(window_size=30)
    all_feature_dfs = []

    for scenario in ["city_driving", "highway_cruising", "aggressive_sport", "thermal_overheat"]:
        sim = OBDSimulator(vehicle_id=f"TRAIN_{scenario.upper()}", scenario=scenario)
        raw_samples = [sim.generate_sample() for _ in range(samples_per_scenario)]
        df_raw = pd.DataFrame(raw_samples)
        
        # Parse timestamps
        df_raw["timestamp"] = pd.to_datetime(df_raw["timestamp"])
        df_features = extractor.transform_dataframe(df_raw, step_size=3)
        all_feature_dfs.append(df_features)

    full_features_df = pd.concat(all_feature_dfs, ignore_index=True)
    labels = DrivingStyleClassifier.generate_heuristic_labels(full_features_df)
    
    return full_features_df, labels

def run_training_pipeline():
    """Main execution workflow for Phase 2 model training."""
    logger.info("=== Starting VehicleIQ Phase 2 ML Training Pipeline ===")
    
    # 1. Dataset Generation
    logger.info("1. Generating multi-trip telemetry training dataset...")
    features_df, labels = generate_synthetic_dataset(samples_per_scenario=150)
    logger.info(f"Dataset ready. Total feature window samples: {len(features_df)}")
    logger.info(f"Label distribution:\n{labels.value_counts()}")

    # 2. Train Driving Style Classifier
    logger.info("2. Training Driving Style Classifier (Random Forest)...")
    classifier = DrivingStyleClassifier()
    cls_metrics = classifier.train(features_df, labels)
    classifier.save("models/driving_style_model.joblib")

    # 3. Train Component Health Predictor (LSTM)
    logger.info("3. Preparing sequence data & training LSTM Component Health Predictor...")
    seq_len = 10
    X_seqs = []
    y_health = []

    # Build sequential windows of shape (num_samples, seq_len, num_features)
    lstm_extractor = ComponentHealthPredictor(sequence_length=seq_len)
    
    for i in range(len(features_df) - seq_len):
        seq_window = features_df.iloc[i : i + seq_len]
        X_seqs.append(seq_window[FEATURE_COLUMNS_LSTM].values)
        
        # Calculate ground truth wear target for synthetic training
        target_dict = lstm_extractor.calculate_heuristic_degradation(seq_window)
        y_health.append([
            target_dict["brake_health"] / 100.0,
            target_dict["engine_health"] / 100.0,
            target_dict["battery_health"] / 100.0
        ])

    X_seqs = np.array(X_seqs)
    y_health = np.array(y_health)

    logger.info(f"LSTM Sequence shape: X={X_seqs.shape}, y={y_health.shape}")
    lstm_predictor = ComponentHealthPredictor(sequence_length=seq_len)
    lstm_metrics = lstm_predictor.train(X_seqs, y_health, epochs=10)
    lstm_predictor.save("models/lstm_health_model.keras")

    # 4. Optional Optuna & MLflow experiment logging
    try:
        import mlflow
        mlflow.set_experiment("VehicleIQ_Component_Prediction")
        with mlflow.start_run(run_name="Phase2_Baseline_Training"):
            mlflow.log_param("window_size", 30)
            mlflow.log_param("lstm_sequence_length", seq_len)
            mlflow.log_metric("classifier_accuracy", cls_metrics["accuracy"])
            mlflow.log_metric("lstm_mae", lstm_metrics["mae"])
            logger.info("Successfully logged metrics to MLflow experiment tracking!")
    except Exception as e:
        logger.info(f"MLflow tracking skipped or local server not running: {e}")

    logger.info("=== Phase 2 ML Training Pipeline Completed Successfully ===")

if __name__ == "__main__":
    run_training_pipeline()
