from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db

from app.models.employee import Employee
from app.models.notification import NotificationType
from app.models.user import User
from app.services.notification import create_notification

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse
)

router = APIRouter(
    prefix="/employees",
    tags=["Employees"]
)


@router.get(
    "/",
    response_model=list[EmployeeResponse]
)
def get_employees(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Employee).all()

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    return employee

@router.post(
    "/",
    response_model=EmployeeResponse
)
def create_employee(
    employee: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_employee = Employee(
        **employee.model_dump()
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Employe cree: {new_employee.id}",
        type=NotificationType.INFO,
        reference_id=new_employee.id
    )

    return new_employee

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,
    employee_data: EmployeeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    for key, value in employee_data.model_dump().items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Employe mis a jour: {employee.id}",
        type=NotificationType.INFO,
        reference_id=employee.id
    )

    return employee

@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(employee)

    db.commit()

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Employe supprime: {employee.id}",
        type=NotificationType.WARNING,
        reference_id=employee.id
    )

    return {
        "message": "Employee deleted successfully"
    }