from pydantic import BaseModel


class StockEntry(BaseModel):
    product_id: int
    warehouse_id: int
    partner_id: int
    quantity: int


class StockExit(BaseModel):
    product_id: int
    warehouse_id: int
    partner_id: int
    quantity: int


class StockTransfer(BaseModel):
    product_id: int

    from_warehouse_id: int
    to_warehouse_id: int

    partner_id: int

    quantity: int