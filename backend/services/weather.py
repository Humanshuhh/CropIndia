import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
import httpx

logger = logging.getLogger("cropindia.weather")
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Optional APIRouter if you mount this file directly in main.py
router = APIRouter(prefix="/api/v1/weather", tags=["Agro Weather Engine"])


async def get_weather_forecast(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """
    Fetches real-time weather, 24-hour hourly outlook, and 7-day agricultural
    forecast matching the KhetSwasthya UI telemetry cards.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "weather_code",
        ],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "precipitation",
            "wind_speed_10m",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "weather_code",
        ],
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            data = response.json()

        current = data.get("current", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        # Compute next 12 hours max rain probability
        next_12h_probs = hourly.get("precipitation_probability", [])[:12]
        max_rain_12h = max(next_12h_probs) if next_12h_probs else 0

        # Spray Advisory Logic:
        # Avoid spraying if:
        # 1. Rain probability in next 12h >= 30%
        # 2. Currently raining (> 0 mm)
        # 3. Wind speed > 15 km/h (spray drift risk)
        wind = current.get("wind_speed_10m", 0.0)
        curr_rain = current.get("precipitation", 0.0)
        safe_to_spray = (max_rain_12h < 30) and (wind < 15.0) and (curr_rain == 0.0)

        daily_dates = daily.get("time", [])
        daily_list: List[Dict[str, Any]] = []
        for i in range(len(daily_dates)):
            daily_list.append(
                {
                    "date": daily_dates[i],
                    "temp_max_c": daily.get("temperature_2m_max", [])[i],
                    "temp_min_c": daily.get("temperature_2m_min", [])[i],
                    "rain_chance_max_pct": daily.get("precipitation_probability_max", [])[i],
                    "total_precipitation_mm": daily.get("precipitation_sum", [])[i],
                    "weather_code": daily.get("weather_code", [])[i],
                }
            )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone", "auto"),
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "humidity_pct": current.get("relative_humidity_2m"),
                "precipitation_mm": curr_rain,
                "wind_speed_kmh": wind,
                "weather_code": current.get("weather_code"),
                "next_12h_rain_chance_pct": max_rain_12h,
                "spray_advisory": "SAFE_TO_SPRAY" if safe_to_spray else "DO_NOT_SPRAY",
            },
            "daily_forecast": daily_list,
        }

    except Exception as exc:
        logger.warning(f"Weather lookup failed: {exc}")
        return None


# Backward-compatible function for existing assistant / diagnostic calls
async def get_current_weather(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """Legacy helper returning lightweight current snapshot."""
    forecast = await get_weather_forecast(latitude, longitude)
    if not forecast:
        return None

    curr = forecast.get("current", {})
    return {
        "temperature_c": curr.get("temperature_c"),
        "humidity_pct": curr.get("humidity_pct"),
        "current_precipitation_mm": curr.get("precipitation_mm"),
        "next_12h_rain_chance_pct": curr.get("next_12h_rain_chance_pct"),
        "spray_advisory": curr.get("spray_advisory"),
    }


# Router endpoint queried by KhetSwasthya.tsx
@router.get("/forecast")
async def get_forecast_endpoint(
    lat: float = Query(..., description="Field latitude coordinate", ge=-90.0, le=90.0),
    lon: float = Query(..., description="Field longitude coordinate", ge=-180.0, le=180.0),
):
    """
    Supplies the live agrometeorological feed for KhetSwasthya.tsx.
    """
    forecast_data = await get_weather_forecast(lat, lon)
    if not forecast_data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agrometeorological weather feed currently unreachable.",
        )
    return {"status": "success", "data": forecast_data}