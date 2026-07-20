from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.stock.reservation import ProjectStockReservation, ReservationStatus
from app.models.stock.stock import Stock
from pydantic import BaseModel, ConfigDict, computed_field
from datetime import datetime
from typing import List

router = APIRouter(prefix="/stock-reservations", tags=["Stock Reservations"])

class ReservationCreate(BaseModel):
    project_id: int
    product_id: int
    reserved_by_id: int | None = None
    quantity: int

class ReservationResponse(ReservationCreate):
    id: int
    status: str
    created_at: datetime
    consumed_at: datetime | None = None
    
    @computed_field
    def product_name(self) -> str | None:
        return self.product.name if getattr(self, "product", None) else None

    model_config = ConfigDict(from_attributes=True)

@router.get("/", response_model=List[ReservationResponse])
def get_reservations(db: Session = Depends(get_db)):
    return db.query(ProjectStockReservation).options(joinedload(ProjectStockReservation.product)).all()

@router.post("/", response_model=ReservationResponse)
def create_reservation(res: ReservationCreate, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.product_id == res.product_id).first()
    
    if not stock or stock.quantity < res.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available for reservation")
        
    db_res = ProjectStockReservation(
        project_id=res.project_id,
        product_id=res.product_id,
        reserved_by_id=res.reserved_by_id,
        quantity=res.quantity
    )
    db.add(db_res)
    
    # Deduct available stock
    stock.quantity -= res.quantity
    
    db.commit()
    db.refresh(db_res)
    return db_res

@router.post("/{reservation_id}/consume", response_model=ReservationResponse)
def consume_reservation(reservation_id: int, db: Session = Depends(get_db)):
    db_res = db.query(ProjectStockReservation).filter(ProjectStockReservation.id == reservation_id).first()
    if not db_res:
        raise HTTPException(status_code=404, detail="Reservation not found")
        
    if db_res.status not in [ReservationStatus.PENDING, ReservationStatus.APPROVED]:
        raise HTTPException(status_code=400, detail="Reservation cannot be consumed in its current state")
        
    db_res.status = ReservationStatus.CONSUMED
    db_res.consumed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_res)
    return db_res
