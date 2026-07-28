"""
VehicleIQ Configuration Manager
Handles environment variables and configuration settings for data ingestion and database connections.
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


class Settings:
    """Application settings loaded from environment variables or sensible defaults."""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database configuration
    # Default to local SQLite database file
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "vehicleiq_dev.db"))
    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "vehicleiq")

    @property
    def DATABASE_URL(self) -> str:
        """Returns SQLAlchemy database URL based on selected DB_TYPE."""
        if self.DB_TYPE.lower() == "postgres":
            return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        # SQLite default
        return f"sqlite:///{self.SQLITE_DB_PATH}"

    # OBD Data Source
    INGESTION_MODE: str = os.getenv("INGESTION_MODE", "simulation")  # 'simulation' or 'live'
    OBD_PORT: str = os.getenv("OBD_PORT", "COM3")  # Windows serial port or Bluetooth MAC/COM
    OBD_BAUDRATE: int = int(os.getenv("OBD_BAUDRATE", "38400"))
    
    # Ingestion rate (seconds between readings)
    SAMPLE_INTERVAL_SEC: float = float(os.getenv("SAMPLE_INTERVAL_SEC", "1.0"))
    BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "10"))  # write to DB every N records

settings = Settings()
