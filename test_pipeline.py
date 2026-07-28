"""
VehicleIQ Pipeline Verification Test Suite
Automated verification tests for Phase 1 Data Pipeline & OBD-II Integration.
"""

import os
import unittest
from datetime import datetime
import pandas as pd

from config import settings
from obd_simulator import OBDSimulator
from obd_reader import SimulatedOBDReader, get_obd_reader
from data_pipeline import OBDDataPipeline
from database import init_db, save_telemetry_df, get_recent_telemetry, OBDTelemetry, SessionLocal

class TestVehicleIQPipeline(unittest.TestCase):

    def setUp(self):
        """Setup test environment and temporary SQLite DB."""
        settings.DB_TYPE = "sqlite"
        settings.SQLITE_DB_PATH = "test_vehicleiq.db"
        if os.path.exists("test_vehicleiq.db"):
            try:
                os.remove("test_vehicleiq.db")
            except Exception:
                pass
        init_db()

    def tearDown(self):
        """Cleanup test database file."""
        if os.path.exists("test_vehicleiq.db"):
            try:
                os.remove("test_vehicleiq.db")
            except Exception:
                pass

    def test_01_obd_simulator_scenarios(self):
        """Verify simulator generates plausible readings across all scenarios."""
        for scenario in ["city_driving", "highway_cruising", "aggressive_sport", "thermal_overheat"]:
            sim = OBDSimulator(vehicle_id="TEST_VEH", scenario=scenario)
            sample = sim.generate_sample()
            
            self.assertIn("rpm", sample)
            self.assertIn("speed_kph", sample)
            self.assertIn("coolant_temp_c", sample)
            self.assertIn("battery_voltage", sample)
            self.assertEqual(sample["scenario"], scenario)
            
            # Check physical limits
            if sample["rpm"] is not None:
                self.assertGreaterEqual(sample["rpm"], 0.0)
                self.assertLessEqual(sample["rpm"], 8000.0)

    def test_02_obd_reader_abstraction(self):
        """Verify OBD reader factory and interface."""
        reader = get_obd_reader(mode="simulation", scenario="highway_cruising")
        self.assertTrue(reader.connect())
        
        sample = reader.read_sensor_data()
        self.assertIsNotNone(sample)
        self.assertIn("speed_kph", sample)
        reader.disconnect()

    def test_03_data_pipeline_cleaning(self):
        """Verify pipeline cleans missing values and clips outliers."""
        raw_samples = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "vehicle_id": "TEST_001",
                "rpm": 12000.0,  # Outlier > 9000
                "speed_kph": -50.0,  # Outlier < 0
                "coolant_temp_c": None,  # Missing -> Impute
                "throttle_pos_pct": 25.0,
                "short_fuel_trim_pct": 1.5,
                "long_fuel_trim_pct": 2.0,
                "battery_voltage": 14.1,
                "maf_g_s": 12.0,
                "scenario": "test",
            }
        ]

        pipeline = OBDDataPipeline()
        df = pipeline.clean_batch(raw_samples)

        self.assertEqual(len(df), 1)
        # Outlier clipping check
        self.assertEqual(df.loc[0, "rpm"], 9000.0)
        self.assertEqual(df.loc[0, "speed_kph"], 0.0)
        # Missing value imputation check
        self.assertEqual(df.loc[0, "coolant_temp_c"], 90.0)

    def test_04_database_persistence(self):
        """Verify end-to-end saving and retrieval of telemetry in database."""
        pipeline = OBDDataPipeline()
        sim = OBDSimulator(vehicle_id="DB_TEST_VEH", scenario="city_driving")
        raw_batch = [sim.generate_sample() for _ in range(15)]
        
        df = pipeline.clean_batch(raw_batch)
        saved_count = save_telemetry_df(df)
        self.assertEqual(saved_count, 15)

        recent = get_recent_telemetry(limit=50)
        self.assertGreaterEqual(len(recent), 15)
        db_veh_ids = [r["vehicle_id"] for r in recent]
        self.assertIn("DB_TEST_VEH", db_veh_ids)

if __name__ == "__main__":
    unittest.main()
