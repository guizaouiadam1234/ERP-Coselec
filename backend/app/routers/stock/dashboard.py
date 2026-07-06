from fastapi import (
    APIRouter,
    Depends
)

from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db

from app.models.stock.product import Product
from app.models.stock.stock import Stock
from app.models.user import User

from app.schemas.stock.dashboard import (
    DashboardResponse
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/",
    response_model=DashboardResponse
)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    products = db.query(Product).all()

    stocks = db.query(Stock).all()

    total_quantity = sum(
        stock.quantity
        for stock in stocks
    )

    total_value = 0

    low_stock_count = 0

    out_of_stock_count = 0

    product_map = {
        product.id: product
        for product in products
    }

    for stock in stocks:

        product = product_map.get(
            stock.product_id
        )

        if not product:
            continue

        total_value += (
            stock.quantity *
            product.unit_price
        )

        if stock.quantity == 0:
            out_of_stock_count += 1

        if stock.quantity <= product.minimum_stock:
            low_stock_count += 1

    return DashboardResponse(
        products=len(products),

        stock_rows=len(stocks),

        total_quantity=total_quantity,

        total_value=total_value,

        low_stock_count=low_stock_count,

        out_of_stock_count=out_of_stock_count
    )
