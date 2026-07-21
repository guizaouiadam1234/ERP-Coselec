from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from sqlalchemy import or_, cast, String
from app.services.pdf_generator import generate_caisse_pdf
from app.services.storage import get_file_url_from_minio
from app.models.caisse_voucher import CaisseVoucher

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

class CaisseVoucherResponse(BaseModel):
    id: int
    num: Optional[str]
    affaire: Optional[str]
    cia: Optional[str]
    depenses: List[CaisseRow]
    recettes: List[CaisseRow]
    pdf_url: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[CaisseVoucherResponse])
def get_caisse_vouchers(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(CaisseVoucher)
    if search:
        search_term = search.replace("PC-", "")
        query = query.filter(
            or_(
                cast(CaisseVoucher.id, String).ilike(f"%{search_term}%"),
                cast(CaisseVoucher.num, String).ilike(f"%{search}%"),
                cast(CaisseVoucher.affaire, String).ilike(f"%{search}%"),
                cast(CaisseVoucher.cia, String).ilike(f"%{search}%"),
                cast(CaisseVoucher.created_at, String).ilike(f"%{search}%")
            )
        )
    return query.order_by(CaisseVoucher.id.desc()).all()

@router.post("/generate")
def generate_caisse(payload: CaisseRequest, db: Session = Depends(get_db)):
    pdf_path = generate_caisse_pdf(payload.dict())
    if not pdf_path:
        return {"error": "Failed to generate PDF"}
        
    pdf_url = get_file_url_from_minio(pdf_path)
    
    # Persist to DB
    voucher = CaisseVoucher(
        num=payload.num,
        affaire=payload.affaire,
        cia=payload.cia,
        depenses=[row.dict() for row in payload.depenses],
        recettes=[row.dict() for row in payload.recettes],
        pdf_url=pdf_url
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    
    return {"pdf_url": pdf_url, "voucher_id": voucher.id}
