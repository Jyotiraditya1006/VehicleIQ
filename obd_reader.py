"""
VehicleIQ OBD Reader Interface
Provides abstract and concrete OBD reader interfaces for both physical ELM327 Bluetooth dongles
and high-fidelity Python telemetry simulators.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, Optional
from config import settings
from obd_simulator import OBDSimulator

logger = logging.getLogger("VehicleIQ.OBDReader")

class BaseOBDReader(ABC):
    """Abstract interface for reading OBD-II sensor streams."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to OBD-II data source."""
        pass

    @abstractmethod
    def read_sensor_data(self) -> Optional[Dict[str, Any]]:
        """Read latest frame of sensor PIDs."""
        pass

    @abstractmethod
    def disconnect(self):
        """Cleanly close connection."""
        pass


class SimulatedOBDReader(BaseOBDReader):
    """Data reader implementation connected to OBDSimulator."""

    def __init__(self, vehicle_id: str = "VEHICLE_001", scenario: str = "city_driving"):
        self.simulator = OBDSimulator(vehicle_id=vehicle_id, scenario=scenario)
        self.is_connected = False

    def connect(self) -> bool:
        logger.info(f"Connected to OBD Simulator (Vehicle: {self.simulator.vehicle_id}, Scenario: {self.simulator.scenario})")
        self.is_connected = True
        return True

    def read_sensor_data(self) -> Optional[Dict[str, Any]]:
        if not self.is_connected:
            logger.error("Cannot read data: Simulated OBD Reader is not connected.")
            return None
        return self.simulator.generate_sample()

    def set_scenario(self, scenario: str):
        self.simulator.set_scenario(scenario)

    def disconnect(self):
        logger.info("Disconnected from OBD Simulator.")
        self.is_connected = False


class PhysicalOBDReader(BaseOBDReader):
    """
    Data reader implementation for physical ELM327 Bluetooth OBD-II dongles.
    Uses the `obd` library to query standard PIDs.
    """

    def __init__(self, port: str = settings.OBD_PORT, baudrate: int = settings.OBD_BAUDRATE):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.is_connected = False

    def connect(self) -> bool:
        try:
            import obd
            logger.info(f"Attempting Bluetooth ELM327 connection on port {self.port} at {self.baudrate} baud...")
            self.connection = obd.OBD(portstr=self.port, baudrate=self.baudrate, fast=False)
            
            if self.connection.is_connected():
                logger.info(f"Successfully connected to physical vehicle OBD-II interface on {self.port}!")
                self.is_connected = True
                return True
            else:
                logger.warning(f"Could not connect to physical ELM327 on {self.port}. Vehicle ignition may be off or Bluetooth pair missing.")
                self.is_connected = False
                return False
        except Exception as e:
            logger.error(f"Error opening physical OBD connection: {e}")
            self.is_connected = False
            return False

    def read_sensor_data(self) -> Optional[Dict[str, Any]]:
        if not self.is_connected or not self.connection:
            logger.error("Physical OBD reader is not connected.")
            return None

        try:
            import obd
            from datetime import datetime

            # Query standard PIDs
            cmd_rpm = self.connection.query(obd.commands.RPM)
            cmd_speed = self.connection.query(obd.commands.SPEED)
            cmd_coolant = self.connection.query(obd.commands.COOLANT_TEMP)
            cmd_throttle = self.connection.query(obd.commands.THROTTLE_POS)
            cmd_sft = self.connection.query(obd.commands.SHORT_FUEL_TRIM_1)
            cmd_lft = self.connection.query(obd.commands.LONG_FUEL_TRIM_1)
            cmd_volt = self.connection.query(obd.commands.ELM_VOLTAGE)
            cmd_maf = self.connection.query(obd.commands.MAF)

            sample = {
                "timestamp": datetime.utcnow().isoformat(),
                "vehicle_id": "VEHICLE_REAL",
                "rpm": cmd_rpm.value.magnitude if not cmd_rpm.is_null() else None,
                "speed_kph": cmd_speed.value.magnitude if not cmd_speed.is_null() else None,
                "coolant_temp_c": cmd_coolant.value.magnitude if not cmd_coolant.is_null() else None,
                "throttle_pos_pct": cmd_throttle.value.magnitude if not cmd_throttle.is_null() else None,
                "short_fuel_trim_pct": cmd_sft.value.magnitude if not cmd_sft.is_null() else None,
                "long_fuel_trim_pct": cmd_lft.value.magnitude if not cmd_lft.is_null() else None,
                "battery_voltage": cmd_volt.value.magnitude if not cmd_volt.is_null() else None,
                "maf_g_s": cmd_maf.value.magnitude if not cmd_maf.is_null() else None,
                "scenario": "live_driving",
            }
            return sample
        except Exception as e:
            logger.error(f"Error querying PIDs from physical OBD interface: {e}")
            return None

    def disconnect(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.is_connected = False
        logger.info("Physical OBD connection closed.")


def get_obd_reader(mode: str = settings.INGESTION_MODE, scenario: str = "city_driving") -> BaseOBDReader:
    """Factory function creating requested OBD reader instance."""
    if mode.lower() == "live":
        reader = PhysicalOBDReader()
        if not reader.connect():
            logger.warning("Falling back to Simulated OBD Reader because Physical Reader connection failed.")
            reader = SimulatedOBDReader(scenario=scenario)
            reader.connect()
        return reader
    else:
        reader = SimulatedOBDReader(scenario=scenario)
        reader.connect()
        return reader
