from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.user import User

from app.schemas.stock.stockoperations import (
    StockEntry,
    StockExit,
    StockTransfer
)

from app.services.stockservice import (
    stock_entry,
    stock_exit,
    stock_transfer
)

router = APIRouter(
    prefix="/stock",
    tags=["Stock"]
)

@router.post("/entry")
def create_entry(
    payload: StockEntry,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return stock_entry(
        db,
        payload.product_id,
        payload.warehouse_id,
        payload.partner_id,
        payload.quantity
    )

@router.post("/exit")
def create_exit(
    payload: StockExit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return stock_exit(
        db,
        payload.product_id,
        payload.warehouse_id,
        payload.partner_id,
        payload.quantity
    )

@router.post("/transfer")
def create_transfer(
    payload: StockTransfer,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return stock_transfer(
        db,
        payload.product_id,
        payload.from_warehouse_id,
        payload.to_warehouse_id,
        payload.partner_id,
        payload.quantity
    )

