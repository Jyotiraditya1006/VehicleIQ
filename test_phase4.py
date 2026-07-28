"""
VehicleIQ Phase 4 Verification Test Suite
Automated verification tests for Mobile App, CI/CD, and Deployment blueprints.
"""

import os
import unittest
import json
import yaml

class TestPhase4DeploymentAndMobile(unittest.TestCase):

    def test_01_mobile_app_structure(self):
        """Verify Expo React Native mobile app files exist."""
        self.assertTrue(os.path.exists("mobile/package.json"))
        self.assertTrue(os.path.exists("mobile/app.json"))
        self.assertTrue(os.path.exists("mobile/App.tsx"))

        with open("mobile/package.json", "r") as f:
          pkg = json.load(f)
          self.assertEqual(pkg["name"], "vehicleiq-mobile")

    def test_02_render_and_vercel_blueprints(self):
        """Verify cloud deployment blueprints."""
        self.assertTrue(os.path.exists("render.yaml"))
        self.assertTrue(os.path.exists("vercel.json"))

        with open("vercel.json", "r") as f:
            v_json = json.load(f)
            self.assertEqual(v_json["version"], 2)

    def test_03_github_actions_pipeline(self):
        """Verify GitHub Actions CI/CD workflow definition."""
        self.assertTrue(os.path.exists(".github/workflows/deploy.yml"))

    def test_04_readme_architectural_documentation(self):
        """Verify README.md contains architectural sections and setup guide."""
        self.assertTrue(os.path.exists("README.md"))
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("VehicleIQ", content)
            self.assertIn("Architecture", content)

if __name__ == "__main__":
    unittest.main()
