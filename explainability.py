"""
VehicleIQ Plain-Language Explainability & Solution Guide Module
Translates ML predictions into human-readable alerts AND actionable step-by-step repair solutions,
estimated repair costs, urgency ratings, and recommended replacement parts.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("VehicleIQ.Explainability")

class ExplainabilityEngine:
    """Generates plain-language diagnostic reports and fix solution guides."""

    def __init__(self):
        pass

    def generate_alerts(
        self,
        features: Dict[str, float],
        driving_style_res: Dict[str, Any],
        health_res: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyzes features and predictions to generate detailed problem diagnostic alerts
        along with complete step-by-step repair solutions.
        """
        alerts = []

        # 1. Brake Health Problem & Solution
        brake_score = health_res.get("brake_health", 100.0)
        hard_braking = features.get("hard_braking_rate", 0.0)
        
        if brake_score < 75.0 or hard_braking > 0.05:
            severity = "CRITICAL" if brake_score < 55.0 else "WARNING"
            alerts.append({
                "component": "Brakes",
                "severity": severity,
                "title": f"Accelerated Brake Pad Friction Wear ({brake_score}% Health Remaining)",
                "explanation": (
                    f"Frequent hard braking events detected during recent trips "
                    f"(hard braking rate: {round(hard_braking * 100, 1)}%). Rapid decelerations "
                    f"elevate rotor friction temperature and accelerate pad wear."
                ),
                "solution_title": "Brake Pad Inspection & Progressive Driving Adjustment",
                "diy_fix_steps": [
                    "Inspect brake pad thickness through wheel caliper window (minimum threshold: 3mm).",
                    "Check brake fluid reservoir level under hood and top up with DOT-4 fluid if low.",
                    "Practice gradual coasting to stops to reduce friction heat buildup by up to 40%."
                ],
                "estimated_cost": "$60 - $140 (₹1,800 - ₹4,500)",
                "urgency": "Moderate — Schedule inspection within 500 km",
                "difficulty": "Easy to Moderate DIY",
                "parts_needed": ["Front Ceramic Brake Pads", "DOT-4 Synthetic Brake Fluid"],
            })

        # 2. Engine Thermal Stress Problem & Solution
        engine_score = health_res.get("engine_health", 100.0)
        max_temp = features.get("coolant_temp_max", 90.0)
        high_rpm = features.get("high_rpm_ratio", 0.0)
        thermal_stress = features.get("thermal_stress_index", 0.0)

        if max_temp > 98.0 or thermal_stress > 1.5 or engine_score < 80.0:
            severity = "CRITICAL" if max_temp > 106.0 or engine_score < 50.0 else "WARNING"
            alerts.append({
                "component": "Engine Thermal",
                "severity": severity,
                "title": f"Engine Coolant Temperature Elevation ({round(max_temp, 1)}°C Peak)",
                "explanation": (
                    f"Coolant temperature reached {round(max_temp, 1)}°C while engine operated at high RPM "
                    f"({round(high_rpm * 100, 1)}% of trip duration). Thermal expansion risks cylinder head gasket stress."
                ),
                "solution_title": "Coolant System Flush & Radiator Fan Relay Test",
                "diy_fix_steps": [
                    "Wait for engine to cool completely before opening radiator overflow cap.",
                    "Verify radiator electric cooling fan activates when engine reaches idle operating temperature.",
                    "Inspect coolant hoses for cracks, bulges, or dried residue leaks.",
                    "Perform a 50/50 ethylene glycol coolant flush and bleed air from cooling lines."
                ],
                "estimated_cost": "$35 - $95 (₹1,200 - ₹3,200)",
                "urgency": "HIGH — Inspect before next long highway trip",
                "difficulty": "Easy DIY",
                "parts_needed": ["Pre-mixed 50/50 Engine Coolant", "12V Radiator Fan Relay"],
            })

        # 3. Battery Voltage & Charging Problem & Solution
        battery_score = health_res.get("battery_health", 100.0)
        min_volt = features.get("battery_voltage_min", 14.0)
        volt_std = features.get("battery_voltage_std", 0.0)

        if min_volt < 12.4 or volt_std > 0.35 or battery_score < 80.0:
            severity = "CRITICAL" if min_volt < 11.6 or battery_score < 50.0 else "WARNING"
            alerts.append({
                "component": "Battery & Alternator",
                "severity": severity,
                "title": f"Electrical System Voltage Drop ({round(min_volt, 2)}V Under Load)",
                "explanation": (
                    f"Control module voltage dropped to {round(min_volt, 2)}V while driving (normal range: 13.8V-14.4V). "
                    f"Voltage fluctuations indicate battery internal resistance build-up or alternator belt slippage."
                ),
                "solution_title": "Terminal Corrosion Cleaning & Alternator Load Test",
                "diy_fix_steps": [
                    "Clean lead battery terminals with baking soda and wire brush to remove white sulfate corrosion.",
                    "Ensure terminal clamps are torqued tightly to eliminate high-resistance connections.",
                    "Test alternator charging output across terminals with a digital multimeter while engine is idling (should read > 13.5V)."
                ],
                "estimated_cost": "$15 - $110 (₹500 - ₹3,500)",
                "urgency": "Immediate — Risk of non-start in cold weather",
                "difficulty": "Easy DIY",
                "parts_needed": ["Terminal Cleaner Spray", "12V 60Ah AGM Automotive Battery (optional)"],
            })

        # 4. Driving Style Optimization Guide
        style = driving_style_res.get("predicted_style", "moderate")
        behavior_score = driving_style_res.get("driving_behavior_score", 75.0)

        style_solutions = {
            "gentle": {
                "title": "Optimized Driving Habit Maintained",
                "explanation": "Smooth acceleration and low braking frequency preserve brake pads and optimize fuel efficiency by ~15%.",
                "solution_title": "Maintain Preventive Maintenance Schedule",
                "steps": [
                    "Rotate tires every 10,000 km for even tread wear.",
                    "Check tire pressure monthly to maintain optimal rolling resistance."
                ],
                "cost": "$0 (Habit Optimization)",
                "urgency": "Routine Care",
                "difficulty": "None",
                "parts": ["None"],
            },
            "moderate": {
                "title": "Moderate Driving Profile with Periodic Heavy Throttle",
                "explanation": "Balanced driving profile with occasional high-rpm accelerations. Minor acceleration spikes increase wear rate by ~1.3x.",
                "solution_title": "Throttle Smoothing & Engine Oil Quality Check",
                "steps": [
                    "Use smooth, progressive throttle pedal inputs rather than rapid stomp accelerations.",
                    "Check engine oil dipstick level and color; change oil if dark brown or sludge-like."
                ],
                "cost": "$25 - $45 (₹800 - ₹1,500)",
                "urgency": "Routine",
                "difficulty": "Easy DIY",
                "parts": ["Synthetic Engine Oil 5W-30", "Oil Filter"],
            },
            "aggressive": {
                "title": "Aggressive Driving Habits Increasing Wear Rate by 2.4x",
                "explanation": "Repeated hard braking, sharp acceleration bursts, and high-RPM gear shifts accelerate pad wear and engine heat stress.",
                "solution_title": "Behavioral Driving Smoothing & Component Relief Plan",
                "steps": [
                    "Adopt 3-second follow distance to anticipate traffic stops without emergency braking.",
                    "Shift gears earlier (below 2,500 RPM) to keep engine operating in efficient powerband.",
                    "Allow engine to idle for 30 seconds before shutoff after spirited driving."
                ],
                "cost": "$0 (Habit Adjustment Saves ~$400/yr in repairs)",
                "urgency": "Immediate Behavioral Adjustment",
                "difficulty": "Habit Shift",
                "parts": ["None"],
            },
        }

        active_style_sol = style_solutions.get(style, style_solutions["moderate"])

        alerts.append({
            "component": "Driving Profile",
            "severity": "INFO",
            "title": f"Driving Behavior: {style.upper()} (Score: {behavior_score}/100)",
            "explanation": active_style_sol["explanation"],
            "solution_title": active_style_sol["solution_title"],
            "diy_fix_steps": active_style_sol["steps"],
            "estimated_cost": active_style_sol["cost"],
            "urgency": active_style_sol["urgency"],
            "difficulty": active_style_sol["difficulty"],
            "parts_needed": active_style_sol["parts"],
        })

        return alerts

    def generate_full_report(
        self,
        vehicle_id: str,
        features: Dict[str, float],
        driving_style_res: Dict[str, Any],
        health_res: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates full diagnostic report with problem & solution guides."""
        alerts = self.generate_alerts(features, driving_style_res, health_res)
        
        overall_health = round(
            (health_res.get("brake_health", 100) + health_res.get("engine_health", 100) + health_res.get("battery_health", 100)) / 3.0,
            1
        )

        return {
            "vehicle_id": vehicle_id,
            "overall_health_score": overall_health,
            "driving_style": driving_style_res.get("predicted_style", "moderate"),
            "driving_behavior_score": driving_style_res.get("driving_behavior_score", 75.0),
            "component_scores": health_res,
            "plain_language_alerts": alerts,
            "summary_text": (
                f"VehicleIQ Diagnostic Analysis for {vehicle_id}: Overall Health {overall_health}%. "
                f"Generated {len(alerts)} diagnostic findings with step-by-step repair solutions."
            ),
        }
