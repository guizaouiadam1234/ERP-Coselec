from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    Enum,
)

from app.database import Base

from app.enums.movement_type import MovementType


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    warehouse_id = Column(
        Integer,
        ForeignKey("warehouses.id"),
        nullable=False
    )

    partner_id = Column(
        Integer,
        ForeignKey("partners.id"),
        nullable=False
    )

    type = Column(
        Enum(MovementType),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )