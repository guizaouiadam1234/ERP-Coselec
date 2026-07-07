from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user, check_permission
from app.database import get_db

from app.models.stock.warehouse import Warehouse
from app.models.user import User

from app.schemas.stock.warehouse import (
    WarehouseCreate,
    WarehouseResponse
)

router = APIRouter(
    prefix="/warehouses",
    tags=["Warehouses"]
)


@router.post(
    "/",
    response_model=WarehouseResponse
)
def create_warehouse(
    warehouse: WarehouseCreate,
    _: None = Depends(check_permission("stock.create")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    existing = (
        db.query(Warehouse)
        .filter(Warehouse.code == warehouse.code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Warehouse already exists"
        )

    new_warehouse = Warehouse(
        **warehouse.model_dump()
    )

    db.add(new_warehouse)
    db.commit()
    db.refresh(new_warehouse)

    return new_warehouse


@router.get(
    "/",
    response_model=list[WarehouseResponse]
)
def get_warehouses(
    _: None = Depends(check_permission("stock.read")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return db.query(Warehouse).all()