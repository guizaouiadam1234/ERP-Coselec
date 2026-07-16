from datetime import datetime
import os
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security.auth import get_current_user, check_permission
from app.modules.users.models.user import User
from app.modules.users.models.employee import Employee
from app.models.hr.leave_request import LeaveRequest, LeaveStatus
from app.schemas.hr.hr import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse
from app.services.pdf_generator import generate_leave_certificate

router = APIRouter(prefix="/leave-requests", tags=["Leave Requests"])

@router.get("/", response_model=list[LeaveRequestResponse])
def get_leave_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(LeaveRequest).all()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LeaveRequestResponse)
def create_leave_request(
    request_data: LeaveRequestCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == request_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    new_request = LeaveRequest(**request_data.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Generate PDF
    pdf_path = generate_leave_certificate(new_request, employee)
    if pdf_path:
        new_request.pdf_url = pdf_path
        db.commit()
        db.refresh(new_request)

    return new_request

@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db.delete(request)
    db.commit()
    return None

@router.get("/{request_id}/certificate")
def download_leave_certificate(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.get(LeaveRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if not request.pdf_url or not os.path.exists(request.pdf_url):
        employee = db.query(Employee).filter(Employee.id == request.employee_id).first()
        pdf_path = generate_leave_certificate(request, employee)
        if pdf_path:
            request.pdf_url = pdf_path
            db.commit()
            db.refresh(request)
        else:
            raise HTTPException(status_code=404, detail="Certificate not found")

    employee = db.query(Employee).filter(Employee.id == request.employee_id).first()
    emp_name = f"{employee.first_name} {employee.last_name}" if hasattr(employee, 'first_name') else employee.name
    emp_name_clean = emp_name.replace(" ", "_").lower()
    
    return FileResponse(
        path=request.pdf_url,
        media_type="application/pdf",
        filename=f"conge_{emp_name_clean}_{datetime.now().strftime('%Y%m%d')}.pdf"
    )
