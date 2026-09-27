from fastapi import APIRouter, HTTPException, status
from backend.schemas.Farmer_schemas import FarmerSchema
from backend.database.firebase import get_firestore_db
from backend.database.firestore_crud import save_farmer_profile

router = APIRouter(prefix="/api/v1/farmer", tags=["Farmer Profile Database"])

@router.post("")
@router.post("/")
def update_farmer_profile(farmer_data: FarmerSchema):
    """Saves or updates the extended farmer profile in Firestore."""
    # Reuses the exact database logic your teammate wrote in firestore_crud.py
    success = save_farmer_profile(farmer_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save profile to Firestore database."
        )
    return {
        "status": "success", 
        "message": "Profile synced successfully", 
        "data": farmer_data.model_dump() 
    }

@router.get("/{farmer_id}")
def get_farmer(farmer_id: str):
    """Fetches the full farmer profile from Firestore."""
    db = get_firestore_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    doc = db.collection("farmers").document(farmer_id).get()
    if doc.exists:
        return doc.to_dict()
    
    raise HTTPException(status_code=404, detail="Farmer profile not found in database")