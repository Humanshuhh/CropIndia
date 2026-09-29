from pydantic import BaseModel, Field
from typing import Optional, List

class FarmerSchema(BaseModel):
    farmer_id: Optional[str] = Field(default=None, description="Unique ID for the farmer")
    name: str
    phone: str
    state: str
    district: str
    language: str = "en"
    # --- FIXED: Support both 'pin' and 'mpin' to prevent null database values ---
    pin: Optional[str] = Field(default=None, description="4-Digit PIN")
    mpin: Optional[str] = Field(default=None, description="4-Digit MPIN for authentication")
    
    # --- Extended Profile Fields for Database Sync ---
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    land_area: Optional[float] = None
    primary_crops: Optional[str] = None
    agro_climatic_zone: Optional[str] = None