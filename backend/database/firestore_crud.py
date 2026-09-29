# backend/database/firestore_crud.py

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from backend.database.firebase import get_firestore_db
from backend.schemas.diagnosis_schemas import CropDiagnosisResponse
from backend.schemas.Farmer_schemas import FarmerSchema
from backend.schemas.soil_schemas import RegenerativeActionPlan, SoilHealthCardInput
from backend.schemas.warning_schemas import EarlyWarningAdvisory

logger = logging.getLogger("kisan_sahayak.firestore")


def save_farmer_profile(farmer_data: FarmerSchema) -> bool:
    """Saves or updates the main farmer profile in Firestore."""
    db = get_firestore_db()
    if not db:
        return False

    try:
        db.collection("farmers").document(farmer_data.farmer_id).set(
            farmer_data.model_dump(), merge=True
        )
        return True
    except Exception as e:
        logger.error(f"Error saving farmer profile: {e}")
        return False


def get_registered_farmers() -> List[Dict[str, Any]]:
    """Retrieves all registered farmer profiles for telemetry and background scans."""
    db = get_firestore_db()
    if not db:
        return []

    try:
        docs = db.collection("farmers").stream()
        return [{"farmer_id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        logger.error(f"Error fetching registered farmers: {e}")
        return []


def save_soil_record(
    farmer_id: str,
    record_id: Optional[str],
    soil_input: Union[SoilHealthCardInput, Dict[str, Any]],
    plan: Union[RegenerativeActionPlan, Dict[str, Any]],
) -> Optional[str]:
    """Combines soil metrics and the AI action plan into one Firestore document."""
    db = get_firestore_db()
    if not db:
        return None

    doc_id = record_id or f"soil_{uuid.uuid4().hex[:10]}"
    input_data = soil_input.model_dump() if hasattr(soil_input, "model_dump") else soil_input
    plan_data = plan.model_dump() if hasattr(plan, "model_dump") else plan

    document_data = {
        "id": doc_id,
        "farmer_id": farmer_id or "default_farmer",
        "category": "SOIL_HEALTH",
        "raw_metrics": input_data,
        "regenerative_plan": plan_data,
        "summary": plan_data.get("spoken_summary") or plan_data.get("soil_health_assessment", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        db.collection("soil_health_records").document(doc_id).set(document_data)
        logger.info(f"Saved soil health record {doc_id} to Firestore.")
        return doc_id
    except Exception as e:
        logger.error(f"Error saving soil record: {e}")
        return None


def save_leaf_diagnostic(
    farmer_id: str,
    diagnostic_id: Optional[str] = None,
    diagnosis: Union[CropDiagnosisResponse, Dict[str, Any], Any] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Optional[str]:
    """Saves the vision model's output and eco-friendly remedies into leaf_diagnostics."""
    db = get_firestore_db()
    if not db:
        return None

    doc_id = diagnostic_id or f"diag_{uuid.uuid4().hex[:10]}"
    diag_data = diagnosis.model_dump() if hasattr(diagnosis, "model_dump") else (diagnosis or {})

    document_data = {
        "id": doc_id,
        "farmer_id": farmer_id or "default_farmer",
        "category": "LEAF_DISEASE",
        "crop_name": diag_data.get("crop_name") or "Unknown Crop",
        "detected_condition": diag_data.get("detected_condition") or diag_data.get("disease_name", "Unknown Condition"),
        "confidence_level": diag_data.get("confidence_level", "MEDIUM"),
        "underlying_cause": diag_data.get("underlying_cause", ""),
        "diagnosis_result": diag_data,
        "spoken_summary": diag_data.get("spoken_summary", ""),
        "latitude": latitude,
        "longitude": longitude,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        db.collection("leaf_diagnostics").document(doc_id).set(document_data)
        logger.info(f"Saved leaf diagnostic {doc_id} to Firestore.")
        return doc_id
    except Exception as e:
        logger.error(f"Error saving leaf diagnostic: {e}")
        return None


def save_early_warning_firestore(
    warning_id: str,
    farmer_id: str,
    latitude: float,
    longitude: float,
    zone: str,
    advisory: Union[EarlyWarningAdvisory, Dict[str, Any]],
) -> bool:
    """
    Saves the early warning advisory to Firestore for the frontend UI.
    Accepts either an EarlyWarningAdvisory Pydantic model or a dumped dict.
    """
    db = get_firestore_db()
    if not db:
        return False

    advisory_dict = (
        advisory.model_dump()
        if isinstance(advisory, EarlyWarningAdvisory)
        else advisory
    )

    document_data = {
        "warning_id": warning_id,
        "farmer_id": farmer_id,
        "latitude": latitude,
        "longitude": longitude,
        "zone": zone,
        "analysis": advisory_dict,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        db.collection("early_warnings").document(warning_id).set(document_data)
        return True
    except Exception as e:
        logger.error(f"Firestore save error: {e}")
        return False


def get_admin_profile(username_or_email: str) -> Optional[Dict[str, Any]]:
    """Retrieves an admin profile by email or document ID."""
    db = get_firestore_db()
    if not db:
        return None

    try:
        doc = db.collection("admins").document(username_or_email).get()
        if doc.exists:
            return {"admin_id": doc.id, **doc.to_dict()}

        query = db.collection("admins").where("email", "==", username_or_email).limit(1).stream()
        for match in query:
            return {"admin_id": match.id, **match.to_dict()}
        return None
    except Exception as e:
        logger.error(f"Error fetching admin profile: {e}")
        return None


def get_admin_dashboard_stats() -> Dict[str, Any]:
    """Aggregates system-wide counts across Firestore collections for the admin dashboard."""
    db = get_firestore_db()
    if not db:
        return {
            "total_farmers": 0,
            "active_warnings": 0,
            "soil_records_count": 0,
            "diagnostics_count": 0,
        }

    try:
        return {
            "total_farmers": len(list(db.collection("farmers").stream())),
            "active_warnings": len(list(db.collection("early_warnings").stream())),
            "soil_records_count": len(list(db.collection("soil_health_records").stream())),
            "diagnostics_count": len(list(db.collection("leaf_diagnostics").stream())),
        }
    except Exception as e:
        logger.error(f"Error aggregating admin stats: {e}")
        return {
            "total_farmers": 0,
            "active_warnings": 0,
            "soil_records_count": 0,
            "diagnostics_count": 0,
        }


def get_combined_farmer_history(farmer_id: str, limit_count: int = 20) -> List[Dict[str, Any]]:
    """Fetches and merges both leaf diagnostics and soil records sorted by created_at."""
    db = get_firestore_db()
    if not db:
        return []

    combined: List[Dict[str, Any]] = []
    try:
        # Fetch Leaf Diagnostics
        leaf_ref = db.collection("leaf_diagnostics")
        leaf_docs = (
            leaf_ref.where("farmer_id", "==", farmer_id).stream()
            if farmer_id and farmer_id != "all"
            else leaf_ref.stream()
        )
        for doc in leaf_docs:
            d = doc.to_dict()
            d["id"] = doc.id
            d["category"] = "LEAF_DISEASE"
            combined.append(d)

        # Fetch Soil Health Records
        soil_ref = db.collection("soil_health_records")
        soil_docs = (
            soil_ref.where("farmer_id", "==", farmer_id).stream()
            if farmer_id and farmer_id != "all"
            else soil_ref.stream()
        )
        for doc in soil_docs:
            d = doc.to_dict()
            d["id"] = doc.id
            d["category"] = "SOIL_HEALTH"
            combined.append(d)

        combined.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return combined[:limit_count]
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return []