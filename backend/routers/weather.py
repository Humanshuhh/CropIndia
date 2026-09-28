# backend/routers/weather.py
from fastapi import APIRouter, HTTPException, Query, status
from backend.services.weather import get_weather_forecast

router = APIRouter(prefix="/api/v1/weather", tags=["Weather"])

@router.get("/forecast")
async def get_forecast(
    lat: float = Query(..., ge=-90.0, le=90.0),
    lon: float = Query(..., ge=-180.0, le=180.0),
):
    data = await get_weather_forecast(lat, lon)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather service unavailable"
        )
    return {"status": "success", "data": data}