# backend/database/bigquery_crud.py

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from backend.database.bigquery import get_bigquery_client
from backend.schemas.climate_schemas import WeatherTelemetry
from backend.schemas.soil_schemas import SoilHealthCardInput

logger = logging.getLogger("kisan_sahayak.bigquery")


def _execute_batch_load(table_name: str, rows: List[Dict[str, Any]], log_entity: str) -> bool:
    """Helper function to handle repetitive BigQuery batch insertion logic."""
    bq = get_bigquery_client()
    if not bq:
        logger.error("BigQuery client not connected.")
        return False

    table_id = f"{bq.project}.crop_data.{table_name}"

    try:
        # Use load_table_from_json for Sandbox tier compatibility
        job = bq.load_table_from_json(rows, table_id)
        job.result()  # Wait for batch ingestion to complete
        logger.info(f"Successfully loaded {len(rows)} {log_entity} to {table_id}")
        return True
    except Exception as e:
        logger.error(f"BigQuery {log_entity} load error: {e}")
        return False


def ingest_historical_weather(weather_data_list: List[WeatherTelemetry]) -> bool:
    """Batch loads IMD weather telemetry into BigQuery."""
    if not weather_data_list:
        return True
        
    rows = [weather.model_dump() for weather in weather_data_list]
    return _execute_batch_load("historical_weather", rows, "weather records")


def ingest_bulk_shc(soil_data_list: List[SoilHealthCardInput]) -> bool:
    """Batch loads Soil Health Cards into BigQuery for regional analytics."""
    if not soil_data_list:
        return True
        
    rows = [soil.model_dump() for soil in soil_data_list]
    return _execute_batch_load("soil_health_cards", rows, "soil health cards")


def log_warning_bigquery(
    warning_id: str,
    farmer_id: str,
    zone: str,
    risk_level: str,
    stress_type: str,
) -> bool:
    """Logs early warning metrics to BigQuery using batch loading."""
    rows = [
        {
            "warning_id": warning_id,
            "farmer_id": farmer_id,
            "zone": zone,
            "risk_level": risk_level,
            "stress_type": stress_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    ]
    return _execute_batch_load("early_warning_logs", rows, f"warning {warning_id}")