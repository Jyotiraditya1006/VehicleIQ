"""
VehicleIQ Phase 3 FastAPI & Auth Verification Test Suite
Automated verification tests for backend REST endpoints and authentication.
"""

import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

class TestPhase3BackendAPI(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_auth_register_and_login(self):
        """Verify user registration and JWT token login."""
        # 1. Register
        reg_payload = {
            "username": "testdriver",
            "email": "driver@vehicleiq.ai",
            "password": "securepassword123"
        }
        res_reg = self.client.post("/auth/register", json=reg_payload)
        self.assertEqual(res_reg.status_code, 200)
        data_reg = res_reg.json()
        self.assertIn("access_token", data_reg)
        self.assertEqual(data_reg["username"], "testdriver")

        # 2. Login
        login_payload = {
            "username": "testdriver",
            "password": "securepassword123"
        }
        res_login = self.client.post("/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        data_login = res_login.json()
        self.assertIn("access_token", data_login)

    def test_02_telemetry_ingest_endpoint(self):
        """Verify POST /api/v1/ingest receives raw sensor dicts."""
        ingest_payload = {
            "samples": [
                {
                    "vehicle_id": "FASTAPI_TEST",
                    "rpm": 2200.0,
                    "speed_kph": 55.0,
                    "coolant_temp_c": 91.0,
                    "throttle_pos_pct": 25.0,
                    "short_fuel_trim_pct": 0.5,
                    "long_fuel_trim_pct": 1.0,
                    "battery_voltage": 14.1,
                    "maf_g_s": 12.5,
                    "scenario": "city_driving"
                }
            ]
        }
        res = self.client.post("/api/v1/ingest", json=ingest_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["saved_count"], 1)

    def test_03_health_score_endpoint(self):
        """Verify GET /api/v1/health-score returns ML predictions & plain-language alerts."""
        res = self.client.get("/api/v1/health-score?vehicle_id=FASTAPI_TEST")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertIn("overall_health_score", data)
        self.assertIn("driving_style", data)
        self.assertIn("component_scores", data)
        self.assertIn("plain_language_alerts", data)

        # Check component scores structure
        comp_scores = data["component_scores"]
        self.assertIn("brake_health", comp_scores)
        self.assertIn("engine_health", comp_scores)
        self.assertIn("battery_health", comp_scores)

    def test_04_mechanic_report_endpoint(self):
        """Verify GET /api/v1/report returns diagnostic report HTML/JSON."""
        res = self.client.get("/api/v1/report?vehicle_id=FASTAPI_TEST")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        
        self.assertIn("html_report", data)
        self.assertIn("overall_health_score", data)
        self.assertIn("VehicleIQ", data["html_report"])

if __name__ == "__main__":
    unittest.main()
