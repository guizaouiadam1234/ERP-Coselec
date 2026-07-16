from pydantic import BaseModel, Field, condecimal
from datetime import date, datetime
from typing import Optional
from app.modules.requests.models.fuel_request import FuelRequestStatus

class FuelRequestCreate(BaseModel):
    request_date: date
    affaire_no: Optional[str] = None
    dossier_no: Optional[str] = None
    
    objet_deplacement: str
    vehicule_matricule: str
    destination: str
    releve_kilometrique: int = Field(gt=0)
    nombre_jours: int = Field(gt=0)
    
    quantite_carburant: condecimal(ge=0, decimal_places=2)
    employee_id: int

class FuelRequestAction(BaseModel):
    action: str = Field(..., description="'APPROVE' ou 'REJECT'")
    comment: Optional[str] = None

class FuelRequestResponse(FuelRequestCreate):
    id: int
    status: FuelRequestStatus
    employee_name: Optional[str] = None
    manager_id: int
    created_at: datetime
    
    logistics_validator_id: Optional[int]
    logistics_validated_at: Optional[datetime]
    finance_validator_id: Optional[int]
    finance_validated_at: Optional[datetime]
    rejection_comment: Optional[str]
    pdf_url: Optional[str]

    class Config:
        from_attributes = True
