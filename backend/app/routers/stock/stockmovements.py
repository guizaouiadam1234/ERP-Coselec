from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.stock.stockmovement import StockMovement

from app.schemas.stock.stockmovements import (
    StockMovementResponse
)

router = APIRouter(
    prefix="/stock-movements",
    tags=["Stock Movements"]
)


@router.get(
    "/",
    response_model=list[StockMovementResponse]
)
def get_movements(
    product_id: int | None = Query(None),
    warehouse_id: int | None = Query(None),
    partner_id: int | None = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(StockMovement)

    if product_id:
        query = query.filter(
            StockMovement.product_id == product_id
        )

    if warehouse_id:
        query = query.filter(
            StockMovement.warehouse_id == warehouse_id
        )

    if partner_id:
        query = query.filter(
            StockMovement.partner_id == partner_id
        )

    return (
        query
        .order_by(
            StockMovement.created_at.desc()
        )
        .all()
    )