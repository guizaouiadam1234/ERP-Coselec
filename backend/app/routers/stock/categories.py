from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.stock.category import Category

from app.schemas.stock.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get("/", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=201
)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(Category)
        .filter(Category.code == category.code)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Category code already exists"
        )

    new_category = Category(
        **category.model_dump()
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    existing = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    data = category.model_dump(
        exclude_unset=True
    )

    for key, value in data.items():
        setattr(existing, key, value)

    db.commit()
    db.refresh(existing)

    return existing


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully"
    }