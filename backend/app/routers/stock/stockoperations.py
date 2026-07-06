from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.database import get_db

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
    db: Session = Depends(get_db)
):
    return stock_entry(
        db,
        payload.product_id,
        payload.warehouse_id,
        payload.partner_id,
        payload.quantity
    )

@router.post("/entry")
def create_entry(
    payload: StockEntry,
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

