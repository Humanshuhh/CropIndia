# backend/routers/soil.py

import logging
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.database.firestore_crud import save_soil_record
from backend.ml_engine.soil_advisor import soil_advisor_engine

logger = logging.getLogger("cropindia.soil")
router = APIRouter(prefix="/api/v1/soil", tags=["Soil Health & Regenerative Agronomy"])


class SoilHealthInput(BaseModel):
    farmer_id: Optional[str] = Field("default_farmer", description="Farmer ID")
    latitude: float = Field(23.66, description="Latitude of the field")
    longitude: float = Field(86.42, description="Longitude of the field")
    ph: Optional[float] = Field(None, description="Soil pH level (1-14)")
    organic_carbon_percent: Optional[float] = Field(None, description="Soil Organic Carbon % (SOC)")
    nitrogen_kg_ha: Optional[float] = Field(None, description="Available Nitrogen in kg/ha")
    phosphorus_kg_ha: Optional[float] = Field(None, description="Available Phosphorus in kg/ha")
    potassium_kg_ha: Optional[float] = Field(None, description="Available Potassium in kg/ha")
    zinc_ppm: Optional[float] = Field(None, description="Available Zinc in ppm")
    target_language: str = Field("en", description="Target language code (e.g., 'en', 'hi', 'mr')")


class BioAmendment(BaseModel):
    name: str
    target_deficiency: str
    preparation_or_sourcing: str
    dosage_and_application: str


class CropRotationCycle(BaseModel):
    season: str
    recommended_crop: str
    ecological_role: str
    water_requirement: str


class RegenerativeReportResponse(BaseModel):
    soil_health_assessment: str
    synthetic_chemical_alert: Optional[str] = None
    biological_amendments: List[BioAmendment]
    regenerative_crop_rotations: List[CropRotationCycle]
    cultural_water_practices: List[str]
    spoken_summary: str


@router.post("/evaluate", response_model=RegenerativeReportResponse)
async def evaluate_soil_health(payload: SoilHealthInput):
    """
    Evaluates soil parameters, runs Gemini regenerative advisor with fallback,
    and persists the result to Firestore History.
    """
    lang = (payload.target_language or "en").lower().strip()
    soc = payload.organic_carbon_percent if payload.organic_carbon_percent is not None else 0.45
    ph = payload.ph if payload.ph is not None else 6.8
    soc_status = "Critically Deficient" if soc < 0.50 else "Moderate"

    # 1. Try Gemini AI Engine first
    try:
        if soil_advisor_engine.client:
            ai_plan = soil_advisor_engine.evaluate_and_advise(payload)
            # Persist to Firestore
            try:
                save_soil_record(
                    farmer_id=payload.farmer_id or "default_farmer",
                    record_id=None,
                    soil_input=payload,
                    plan=ai_plan,
                )
            except Exception as e:
                logger.warning(f"Could not persist AI soil record: {e}")
            return ai_plan
    except Exception as exc:
        logger.warning(f"Gemini soil advisor failed, using localized rule-based fallback: {exc}")

    # 2. Localized Fallback based on selected language
    if lang == "hi":
        spoken_text = f"किसान भाई, आपकी मिट्टी में जैविक कार्बन {soc}% है जो कि कम है। यूरिया और डीएपी का उपयोग बंद करें। खेत में जीवामृत, ट्राइकोडर्मा और ढैंचा की हरी खाद का प्रयोग करें।"
        assessment = f"मिट्टी का जैविक कार्बन {soc}% ({soc_status}) है और pH {ph} है।"
    elif lang == "mr":
        spoken_text = f"शेतकरी बंधू, तुमच्या मातीमध्ये सेंद्रिय कर्ब {soc}% आहे जे कमी आहे. रासायनिक खतांचा वापर थांबवा. शेतात जीवामृत, ट्रायकोडर्मा आणि तागाचे हिरवे खत वापरा."
        assessment = f"मातीतील सेंद्रिय कर्ब {soc}% ({soc_status}) आहे आणि सामू (pH) {ph} आहे।"
    else:  # English default
        spoken_text = f"Dear farmer, your soil organic carbon is {soc}%, which is {soc_status.lower()}. Avoid synthetic urea and DAP. Apply fermented Jeevamrit, Trichoderma, and green manure like Sesbania."
        assessment = f"Soil Organic Carbon is {soc}% ({soc_status}). Soil pH is {ph}."

    report = RegenerativeReportResponse(
        soil_health_assessment=assessment,
        synthetic_chemical_alert="Zero synthetic chemicals recommended. Avoid Urea and DAP to rebuild soil biology.",
        biological_amendments=[
            BioAmendment(
                name="Fermented Jeevamrit Solution",
                target_deficiency="Depleted Organic Carbon and beneficial bacterial colony collapse",
                preparation_or_sourcing="Ferment indigenous cow dung, urine, jaggery, and pulse flour for 5-7 days.",
                dosage_and_application="200 liters per acre via irrigation or root drenching every 14 days.",
            ),
            BioAmendment(
                name="Trichoderma Enriched FYM",
                target_deficiency="Soil-borne fungal pathogens and low microbial biomass",
                preparation_or_sourcing="Mix 2 kg Trichoderma harzianum into 100 kg moist farmyard manure under shade.",
                dosage_and_application="Broadcast 100 kg per acre before sowing or mulching.",
            ),
        ],
        regenerative_crop_rotations=[
            CropRotationCycle(
                season="Zaid (Summer)",
                recommended_crop="Dhaincha (Sesbania) Green Manure",
                ecological_role="Fixes atmospheric nitrogen and restores organic humus",
                water_requirement="Low",
            ),
            CropRotationCycle(
                season="Kharif",
                recommended_crop="Pearl Millet (Bajra) intercropped with Pigeon Pea (Arhar)",
                ecological_role="Drought resilience and monoculture disruption",
                water_requirement="Low",
            ),
        ],
        cultural_water_practices=[
            "Broadcast dry crop residue mulch to preserve soil moisture.",
            "Adopt minimum tillage along contour lines.",
        ],
        spoken_summary=spoken_text,
    )

    # Persist fallback record to Firestore
    try:
        save_soil_record(
            farmer_id=payload.farmer_id or "default_farmer",
            record_id=None,
            soil_input=payload,
            plan=report,
        )
    except Exception as exc:
        logger.warning(f"Could not persist fallback soil record to history: {exc}")

    return report