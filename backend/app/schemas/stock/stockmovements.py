from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockMovementResponse(BaseModel):
    id: int

    product_id: int
    warehouse_id: int
    partner_id: int

    type: str
    quantity: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
