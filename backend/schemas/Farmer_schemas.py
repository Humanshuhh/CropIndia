from pydantic import BaseModel, Field
from typing import Optional, List

class FarmerSchema(BaseModel):
    farmer_id: Optional[str] = Field(default=None, description="Unique ID for the farmer")
    name: str
    phone: str
    state: str
    district: str
    language: str = "en"
    # --- ADDED: Extended Profile Fields for Database Sync ---
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    land_area: Optional[float] = None
    primary_crops: Optional[str] = None
    agro_climatic_zone: Optional[str] = None

# Schema for Field / Land Details
class FieldSchema(BaseModel):
    field_id: Optional[str] = Field(default=None, description="Unique ID for the field")
    farmer_id: str
    area_acres: float
    soil_type: Optional[str] = None
    crops_grown: List[str] = []

# Schema for Crop Diagnosis Entry
class DiagnosisRecordSchema(BaseModel):
    diagnosis_id: Optional[str] = Field(default=None, description="Unique ID for the diagnosis record")
    farmer_id: str
    image_url: str
    disease_detected: str
    confidence_score: float
    recommended_action: str