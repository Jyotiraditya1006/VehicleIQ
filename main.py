"""
VehicleIQ Data Ingestion Service CLI Runner
Main entry point for starting live or simulated OBD-II telemetry ingestion into SQLite/PostgreSQL.
"""

import argparse
import logging
import sys
import time
from config import settings
from database import init_db, save_telemetry_df, get_recent_telemetry
from obd_reader import get_obd_reader, BaseOBDReader
from data_pipeline import OBDDataPipeline

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VehicleIQ.Main")

def run_ingestion(mode: str = "simulation", scenario: str = "city_driving", total_samples: int = 50, batch_size: int = 10):
    """Executes the data ingestion loop."""
    logger.info("=== Starting VehicleIQ Phase 1 Ingestion Service ===")
    logger.info(f"Mode: {mode} | Scenario: {scenario} | Database Target: {settings.DB_TYPE}")

    # 1. Initialize Database Schema
    init_db()

    # 2. Instantiate OBD Reader & Pipeline
    reader: BaseOBDReader = get_obd_reader(mode=mode, scenario=scenario)
    pipeline = OBDDataPipeline()

    raw_batch = []
    total_saved = 0
    sample_counter = 0

    try:
        while True:
            sample = reader.read_sensor_data()
            if sample:
                raw_batch.append(sample)
                sample_counter += 1
                logger.info(
                    f"[{sample_counter}] Telemetry Sample -> RPM: {sample.get('rpm')} | "
                    f"Speed: {sample.get('speed_kph')} km/h | "
                    f"Temp: {sample.get('coolant_temp_c')} °C | "
                    f"Battery: {sample.get('battery_voltage')} V"
                )

            # Process batch when buffer size reaches batch_size
            if len(raw_batch) >= batch_size:
                cleaned_df = pipeline.clean_batch(raw_batch)
                num_saved = save_telemetry_df(cleaned_df)
                total_saved += num_saved
                raw_batch.clear()

            if total_samples > 0 and sample_counter >= total_samples:
                break

            time.sleep(settings.SAMPLE_INTERVAL_SEC)

        # Process any remaining items in buffer
        if raw_batch:
            cleaned_df = pipeline.clean_batch(raw_batch)
            num_saved = save_telemetry_df(cleaned_df)
            total_saved += num_saved
            raw_batch.clear()

    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user.")
    except Exception as e:
        logger.error(f"Ingestion service encountered error: {e}", exc_info=True)
    finally:
        reader.disconnect()
        logger.info(f"Ingestion complete. Total records stored in DB: {total_saved}")

    # Verify data in DB
    recent = get_recent_telemetry(limit=3)
    logger.info(f"Sample stored DB records verification (showing last {len(recent)}):")
    for rec in recent:
        logger.info(f"  ID {rec['id']} | Time: {rec['timestamp']} | Speed: {rec['speed_kph']} km/h | Temp: {rec['coolant_temp_c']} °C")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VehicleIQ OBD-II Data Ingestion Service")
    parser.add_argument("--mode", choices=["simulation", "live"], default=settings.INGESTION_MODE, help="Ingestion mode")
    parser.add_argument("--scenario", choices=["city_driving", "highway_cruising", "aggressive_sport", "thermal_overheat"], default="city_driving", help="Simulation scenario")
    parser.add_argument("--count", type=int, default=30, help="Number of telemetry samples to ingest (0 for infinite loop)")
    parser.add_argument("--batch-size", type=int, default=settings.BATCH_SIZE, help="Batch size before committing to database")
    
    args = parser.parse_args()
    run_ingestion(mode=args.mode, scenario=args.scenario, total_samples=args.count, batch_size=args.batch_size)
