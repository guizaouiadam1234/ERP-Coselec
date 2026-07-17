from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services.pdf_generator import generate_caisse_pdf
from app.services.storage import get_file_url_from_minio

router = APIRouter(
    prefix="/caisse",
    tags=["Caisse"]
)

class CaisseRow(BaseModel):
    date: str
    designation: str
    montant: str

class CaisseRequest(BaseModel):
    num: Optional[str] = ""
    affaire: Optional[str] = ""
    cia: Optional[str] = ""
    depenses: List[CaisseRow] = []
    recettes: List[CaisseRow] = []

@router.post("/generate")
def generate_caisse(payload: CaisseRequest):
    pdf_path = generate_caisse_pdf(payload.dict())
    if not pdf_path:
        return {"error": "Failed to generate PDF"}
    return {"pdf_url": get_file_url_from_minio(pdf_path)}
