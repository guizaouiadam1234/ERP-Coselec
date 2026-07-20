from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.procurement.purchase import PurchaseRequest, PurchaseOrder, PurchaseOrderLine
from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import List

router = APIRouter(prefix="/procurement", tags=["Procurement"])

class PurchaseRequestCreate(BaseModel):
    project_id: int
    requester_id: int | None = None
    description: str | None = None
    expected_date: date | None = None

class PurchaseRequestResponse(PurchaseRequestCreate):
    id: int
    status: str
    model_config = ConfigDict(from_attributes=True)

class PurchaseOrderCreate(BaseModel):
    purchase_request_id: int | None = None
    supplier_id: int | None = None

class PurchaseOrderResponse(PurchaseOrderCreate):
    id: int
    status: str
    total_amount: float
    model_config = ConfigDict(from_attributes=True)

@router.get("/requests", response_model=List[PurchaseRequestResponse])
def get_purchase_requests(db: Session = Depends(get_db)):
    return db.query(PurchaseRequest).all()

@router.post("/requests", response_model=PurchaseRequestResponse)
def create_purchase_request(req: PurchaseRequestCreate, db: Session = Depends(get_db)):
    db_req = PurchaseRequest(
        project_id=req.project_id,
        requester_id=req.requester_id,
        description=req.description,
        expected_date=req.expected_date
    )
    db.add(db_req)
    try:
        db.commit()
        db.refresh(db_req)
        return db_req
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid project_id or requester_id")

@router.get("/orders", response_model=List[PurchaseOrderResponse])
def get_purchase_orders(db: Session = Depends(get_db)):
    return db.query(PurchaseOrder).all()

@router.post("/orders", response_model=PurchaseOrderResponse)
def create_purchase_order(order: PurchaseOrderCreate, db: Session = Depends(get_db)):
    db_order = PurchaseOrder(
        purchase_request_id=order.purchase_request_id,
        supplier_id=order.supplier_id
    )
    db.add(db_order)
    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid request_id or supplier_id")
