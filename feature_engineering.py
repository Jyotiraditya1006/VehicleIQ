"""
VehicleIQ Feature Engineering Module
Transforms raw time-series OBD-II telemetry into rich sliding-window behavioral features.
"""

import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np

logger = logging.getLogger("VehicleIQ.FeatureEngineering")

class OBDFeatureExtractor:
    """Calculates sliding-window behavior features from clean telemetry DataFrames."""

    def __init__(self, window_size: int = 30):
        self.window_size = window_size

    def extract_window_features(self, df_window: pd.DataFrame) -> Dict[str, float]:
        """
        Extracts single set of behavioral metrics from a dataframe window (e.g. 30 seconds).
        """
        if df_window.empty or len(df_window) < 5:
            # Fallback default feature dictionary
            return {
                "hard_braking_rate": 0.0,
                "hard_accel_rate": 0.0,
                "high_rpm_ratio": 0.0,
                "extreme_rpm_ratio": 0.0,
                "idle_ratio": 0.0,
                "thermal_stress_index": 0.0,
                "coolant_temp_max": 90.0,
                "coolant_temp_slope": 0.0,
                "battery_voltage_min": 14.0,
                "battery_voltage_std": 0.0,
                "fuel_trim_abs_mean": 0.0,
                "speed_mean": 0.0,
                "speed_std": 0.0,
                "throttle_mean": 0.0,
                "throttle_std": 0.0,
                "maf_mean": 3.5,
            }

        # 1. Acceleration & Deceleration deltas (km/h per second assuming 1s sampling)
        speed_diff = df_window["speed_kph"].diff().fillna(0.0)
        
        # Hard braking threshold: drop in speed > 12 km/h per sec
        hard_braking_events = (speed_diff < -12.0).sum()
        hard_braking_rate = float(hard_braking_events / len(df_window))

        # Hard acceleration threshold: gain in speed > 12 km/h per sec
        hard_accel_events = (speed_diff > 12.0).sum()
        hard_accel_rate = float(hard_accel_events / len(df_window))

        # 2. RPM behavior ratios
        high_rpm_mask = df_window["rpm"] > 3500.0
        high_rpm_ratio = float(high_rpm_mask.mean())

        extreme_rpm_mask = df_window["rpm"] > 5000.0
        extreme_rpm_ratio = float(extreme_rpm_mask.mean())

        # 3. Idle ratio (speed == 0 and engine running RPM > 500)
        idle_mask = (df_window["speed_kph"] < 2.0) & (df_window["rpm"] > 500.0)
        idle_ratio = float(idle_mask.mean())

        # 4. Thermal stress cycle index
        # Measures degree-seconds above baseline 98°C threshold
        temp = df_window["coolant_temp_c"]
        overheat_degrees = (temp - 98.0).clip(lower=0.0)
        thermal_stress_index = float(overheat_degrees.sum() / len(df_window))
        coolant_temp_max = float(temp.max())
        
        # Coolant temperature trend slope
        if len(df_window) > 1:
            coolant_temp_slope = float((temp.iloc[-1] - temp.iloc[0]) / len(df_window))
        else:
            coolant_temp_slope = 0.0

        # 5. Electrical System (Battery Voltage)
        battery = df_window["battery_voltage"]
        battery_voltage_min = float(battery.min())
        battery_voltage_std = float(battery.std()) if len(battery) > 1 else 0.0

        # 6. Fuel Trim Imbalance
        sft_abs = df_window["short_fuel_trim_pct"].abs()
        lft_abs = df_window["long_fuel_trim_pct"].abs()
        fuel_trim_abs_mean = float((sft_abs + lft_abs).mean())

        # 7. Speed & Throttle dynamics
        speed_mean = float(df_window["speed_kph"].mean())
        speed_std = float(df_window["speed_kph"].std()) if len(df_window) > 1 else 0.0
        throttle_mean = float(df_window["throttle_pos_pct"].mean())
        throttle_std = float(df_window["throttle_pos_pct"].std()) if len(df_window) > 1 else 0.0
        maf_mean = float(df_window["maf_g_s"].mean())

        return {
            "hard_braking_rate": hard_braking_rate,
            "hard_accel_rate": hard_accel_rate,
            "high_rpm_ratio": high_rpm_ratio,
            "extreme_rpm_ratio": extreme_rpm_ratio,
            "idle_ratio": idle_ratio,
            "thermal_stress_index": thermal_stress_index,
            "coolant_temp_max": coolant_temp_max,
            "coolant_temp_slope": coolant_temp_slope,
            "battery_voltage_min": battery_voltage_min,
            "battery_voltage_std": battery_voltage_std if not np.isnan(battery_voltage_std) else 0.0,
            "fuel_trim_abs_mean": fuel_trim_abs_mean,
            "speed_mean": speed_mean,
            "speed_std": speed_std if not np.isnan(speed_std) else 0.0,
            "throttle_mean": throttle_mean,
            "throttle_std": throttle_std if not np.isnan(throttle_std) else 0.0,
            "maf_mean": maf_mean,
        }

    def transform_dataframe(self, df: pd.DataFrame, step_size: int = 5) -> pd.DataFrame:
        """
        Transforms full continuous telemetry DataFrame into sliding-window feature records.
        """
        if df.empty or len(df) < self.window_size:
            # If smaller than 1 window, compute on whatever data exists
            single_feat = self.extract_window_features(df)
            return pd.DataFrame([single_feat])

        feature_records = []
        for start_idx in range(0, len(df) - self.window_size + 1, step_size):
            window_df = df.iloc[start_idx : start_idx + self.window_size]
            features = self.extract_window_features(window_df)
            # Add metadata from last row in window
            features["timestamp"] = window_df["timestamp"].iloc[-1]
            features["vehicle_id"] = window_df["vehicle_id"].iloc[-1]
            features["scenario"] = window_df["scenario"].iloc[-1]
            feature_records.append(features)

        return pd.DataFrame(feature_records)
