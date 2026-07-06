from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.stock.stock import Stock

from app.schemas.stock.stock import StockResponse


router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)


@router.get("/", response_model=list[StockResponse])
def get_stocks(
    product_id: int | None = Query(None),
    warehouse_id: int | None = Query(None),
    partner_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Stock)

    if product_id:
        query = query.filter(
            Stock.product_id == product_id
        )

    if warehouse_id:
        query = query.filter(
            Stock.warehouse_id == warehouse_id
        )

    if partner_id:
        query = query.filter(
            Stock.partner_id == partner_id
        )

    return query.all()
