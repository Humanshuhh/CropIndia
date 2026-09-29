# backend/main.py

from contextlib import asynccontextmanager
from typing import Any, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from backend.agronomy.telemetry_worker import run_daily_telemetry_scan
from backend.database.firebase import get_firestore_db
from backend.ml_engine.soil_advisor import soil_advisor_engine

# Modular Domain Routers
from backend.routers.admin import router as admin_router
from backend.routers.auth import router as auth_router
from backend.routers.diagnostics import router as diagnostics_router
from backend.routers.early_warning import router as early_warning_router
from backend.routers.farmer_assistant import router as assistant_router
from backend.routers.farmer_profile import router as farmer_profile_router
from backend.routers.history import router as history_router
from backend.routers.soil import router as soil_router
from backend.routers.telemetry import router as telemetry_router
from backend.routers.voice import router as voice_router
from backend.routers.weather import router as weather_router

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown lifecycle.
    Initializes Firestore client and the background agronomic telemetry worker.
    """
    db_client = get_firestore_db()

    # Schedule the background scan to run daily
    scheduler.add_job(
        run_daily_telemetry_scan,
        trigger="interval",
        hours=24,
        args=[db_client],
        id="daily_farm_scan",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] Automated agricultural telemetry worker started.")

    yield

    scheduler.shutdown()
    print("[Scheduler] Automated agricultural telemetry worker shut down.")


app = FastAPI(
    title="Kisan Intelligence Digital Public Good Engine",
    description="Unified agro-climatic, geospatial, and multimodal diagnostic backend for smallholder farmers.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for local development and client consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all domain routers
app.include_router(diagnostics_router)
app.include_router(soil_router)
app.include_router(voice_router)
app.include_router(early_warning_router)
app.include_router(assistant_router)
app.include_router(telemetry_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(history_router)
app.include_router(farmer_profile_router)
app.include_router(weather_router)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root Discovery Endpoint",
    tags=["System Status"],
)
async def root() -> Dict[str, Any]:
    """Root metadata and service discovery."""
    return {
        "network": "CropIndia - Kisan Sahayak Network",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "documentation": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json",
            "auth_signup": "/api/v1/auth/signup",
            "auth_login": "/api/v1/auth/login",
            "admin_metrics": "/api/v1/admin/metrics",
            "diagnose_leaf": "/api/v1/diagnostics/diagnose",
            "soil_evaluate": "/api/v1/soil/evaluate",
            "soil_regenerative_plan": "/api/v1/soil/regenerative-plan",
            "farmer_assistant_query": "/api/v1/farmer/query",
            "history_records": "/api/v1/history/{farmer_id}",
            "weather_forecast": "/api/v1/weather/forecast",
            "voice_languages": "/api/v1/voice/languages",
            "voice_stream": "/api/v1/voice/listen",
            "telemetry_surface_map": "/api/v1/telemetry/sentinel-surface-map",
            "telemetry_zones": "/api/v1/telemetry/agro-climatic-zones",
            "early_warning_alerts": "/api/v1/early-warning/alerts",
        },
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check Probe",
    tags=["System Status"],
)
def health_check() -> Dict[str, Any]:
    """Liveness probe returning engine and database connectivity state."""
    db = get_firestore_db()
    return {
        "status": "healthy",
        "service": "agro-advisory-engine",
        "gemini_configured": bool(getattr(soil_advisor_engine, "client", False)),
        "firestore_connected": db is not None,
    }