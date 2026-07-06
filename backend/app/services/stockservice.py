from fastapi import HTTPException

from app.models.stock.stock import Stock
from app.models.stock.stockmovement import StockMovement

from app.enums.movement_type import MovementType


def get_or_create_stock(
    db,
    product_id,
    warehouse_id,
    partner_id
):
    stock = (
        db.query(Stock)
        .filter(
            Stock.product_id == product_id,
            Stock.warehouse_id == warehouse_id,
            Stock.partner_id == partner_id
        )
        .first()
    )

    if not stock:
        stock = Stock(
            product_id=product_id,
            warehouse_id=warehouse_id,
            partner_id=partner_id,
            quantity=0
        )

        db.add(stock)
        db.flush()

    return stock

def stock_entry(
    db,
    product_id,
    warehouse_id,
    partner_id,
    quantity
):

    stock = get_or_create_stock(
        db,
        product_id,
        warehouse_id,
        partner_id
    )

    stock.quantity += quantity

    movement = StockMovement(
        product_id=product_id,
        warehouse_id=warehouse_id,
        partner_id=partner_id,
        quantity=quantity,
        type=MovementType.ENTRY
    )

    db.add(movement)

    db.commit()

    return stock

def stock_exit(
    db,
    product_id,
    warehouse_id,
    partner_id,
    quantity
):
    stock = get_or_create_stock(
        db,
        product_id,
        warehouse_id,
        partner_id
    )

    if stock.quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    stock.quantity -= quantity

    movement = StockMovement(
        product_id=product_id,
        warehouse_id=warehouse_id,
        partner_id=partner_id,
        quantity=quantity,
        type=MovementType.EXIT
    )

    db.add(movement)

    db.commit()

    return stock

def stock_transfer(
    db,
    product_id,
    from_warehouse_id,
    to_warehouse_id,
    partner_id,
    quantity
):
    origin = get_or_create_stock(
        db,
        product_id,
        from_warehouse_id,
        partner_id
    )

    if origin.quantity < quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock"
        )

    destination = get_or_create_stock(
        db,
        product_id,
        to_warehouse_id,
        partner_id
    )

    origin.quantity -= quantity
    destination.quantity += quantity

    db.add(
        StockMovement(
            product_id=product_id,
            warehouse_id=from_warehouse_id,
            partner_id=partner_id,
            quantity=quantity,
            type=MovementType.TRANSFER_OUT
        )
    )

    db.add(
        StockMovement(
            product_id=product_id,
            warehouse_id=to_warehouse_id,
            partner_id=partner_id,
            quantity=quantity,
            type=MovementType.TRANSFER_IN
        )
    )

    db.commit()

    return {
        "message": "Transfer completed"
    }