"""
VehicleIQ OBD-II Telemetry Simulator
Generates realistic, physically plausible OBD-II sensor streams across various driving scenarios.
"""

from datetime import datetime
import math
import random
from typing import Dict, Any, Generator

class OBDSimulator:
    """Generates continuous realistic OBD-II sensor readings."""
    
    SCENARIOS = ["city_driving", "highway_cruising", "aggressive_sport", "thermal_overheat"]

    def __init__(self, vehicle_id: str = "VEHICLE_001", scenario: str = "city_driving"):
        self.vehicle_id = vehicle_id
        self.scenario = scenario if scenario in self.SCENARIOS else "city_driving"
        self.step_count = 0
        
        # State variables for continuous physics transitions
        self.current_speed = 0.0
        self.current_rpm = 750.0
        self.current_coolant_temp = 88.0
        self.current_battery_voltage = 14.1
        self.current_short_fuel_trim = 0.5
        self.current_long_fuel_trim = 1.2

    def set_scenario(self, scenario: str):
        """Dynamically switch driving scenario."""
        if scenario in self.SCENARIOS:
            self.scenario = scenario

    def generate_sample(self) -> Dict[str, Any]:
        """Generates a single OBD-II sensor sample based on current driving scenario physics."""
        self.step_count += 1
        t = self.step_count

        if self.scenario == "city_driving":
            # Stop-and-go driving pattern
            target_speed = max(0.0, 35.0 + 25.0 * math.sin(t / 10.0) + random.uniform(-5, 5))
            if random.random() < 0.15:  # Red light stop simulation
                target_speed = 0.0
            
            self.current_speed = round(0.7 * self.current_speed + 0.3 * target_speed, 2)
            
            if self.current_speed < 1.0:
                self.current_rpm = round(750.0 + random.uniform(-20, 20), 2)
                throttle = round(random.uniform(0.0, 5.0), 2)
            else:
                self.current_rpm = round(1200.0 + self.current_speed * 35.0 + random.uniform(-100, 100), 2)
                throttle = round(min(100.0, 15.0 + self.current_speed * 0.8 + random.uniform(-5, 5)), 2)

            self.current_coolant_temp = round(88.0 + 3.0 * math.sin(t / 50.0) + random.uniform(-0.5, 0.5), 2)
            self.current_battery_voltage = round(14.0 + random.uniform(-0.2, 0.2), 2)
            self.current_short_fuel_trim = round(random.uniform(-3.0, 3.0), 2)

        elif self.scenario == "highway_cruising":
            # High steady speed, low RPM variance
            target_speed = 105.0 + random.uniform(-3, 3)
            self.current_speed = round(0.9 * self.current_speed + 0.1 * target_speed, 2)
            self.current_rpm = round(2200.0 + (self.current_speed - 100.0) * 20.0 + random.uniform(-30, 30), 2)
            throttle = round(28.0 + random.uniform(-2, 2), 2)
            self.current_coolant_temp = round(91.0 + random.uniform(-0.3, 0.3), 2)
            self.current_battery_voltage = round(14.2 + random.uniform(-0.1, 0.1), 2)
            self.current_short_fuel_trim = round(random.uniform(-1.5, 1.5), 2)

        elif self.scenario == "aggressive_sport":
            # Hard acceleration bursts, high RPM, rapid throttle changes
            if t % 15 < 7:  # Hard acceleration phase
                target_speed = min(160.0, self.current_speed + random.uniform(15, 25))
                self.current_rpm = round(min(6800.0, 3500.0 + random.uniform(1500, 2800)), 2)
                throttle = round(random.uniform(70.0, 98.0), 2)
            else:  # Hard braking phase
                target_speed = max(20.0, self.current_speed - random.uniform(20, 35))
                self.current_rpm = round(max(900.0, 1800.0 + random.uniform(-200, 200)), 2)
                throttle = round(random.uniform(0.0, 10.0), 2)
                
            self.current_speed = round(target_speed, 2)
            self.current_coolant_temp = round(min(108.0, 93.0 + t * 0.15 + random.uniform(-0.5, 0.5)), 2)
            self.current_battery_voltage = round(13.8 + random.uniform(-0.3, 0.3), 2)
            self.current_short_fuel_trim = round(random.uniform(-8.0, 12.0), 2)

        elif self.scenario == "thermal_overheat":
            # Overheating engine simulation & electrical load drop
            self.current_speed = round(45.0 + 10.0 * math.sin(t / 5.0), 2)
            self.current_rpm = round(2100.0 + random.uniform(-100, 100), 2)
            throttle = round(35.0 + random.uniform(-5, 5), 2)
            # Coolant temp steadily climbs past normal (105°C+)
            self.current_coolant_temp = round(95.0 + min(25.0, t * 0.4) + random.uniform(-0.2, 0.5), 2)
            # Battery voltage degradation under heat stress
            self.current_battery_voltage = round(max(11.2, 13.5 - t * 0.05 + random.uniform(-0.1, 0.1)), 2)
            self.current_short_fuel_trim = round(random.uniform(8.0, 18.0), 2)  # Running rich/lean malfunction

        # Mass Air Flow (MAF) calculated dynamically based on RPM and throttle
        # Formula: MAF (g/s) ~ (RPM * Engine Displacement * Volumetric Efficiency * Air Density) / 120
        maf_g_s = round(max(2.0, (self.current_rpm / 1000.0) * (1.0 + throttle / 20.0) * 3.5 + random.uniform(-0.5, 0.5)), 2)
        
        # Long term fuel trim drifts slowly
        self.current_long_fuel_trim = round(0.98 * self.current_long_fuel_trim + 0.02 * (self.current_short_fuel_trim * 0.5), 2)

        # Inject 1% missing value chance to simulate real sensor noise/loss
        sample = {
            "timestamp": datetime.utcnow().isoformat(),
            "vehicle_id": self.vehicle_id,
            "rpm": self.current_rpm if random.random() > 0.01 else None,
            "speed_kph": max(0.0, self.current_speed) if random.random() > 0.01 else None,
            "coolant_temp_c": self.current_coolant_temp,
            "throttle_pos_pct": min(100.0, max(0.0, throttle)),
            "short_fuel_trim_pct": self.current_short_fuel_trim,
            "long_fuel_trim_pct": self.current_long_fuel_trim,
            "battery_voltage": self.current_battery_voltage,
            "maf_g_s": maf_g_s,
            "scenario": self.scenario,
        }
        return sample

    def stream(self, count: int = 100) -> Generator[Dict[str, Any], None, None]:
        """Generator yielding samples continuously."""
        for _ in range(count):
            yield self.generate_sample()
