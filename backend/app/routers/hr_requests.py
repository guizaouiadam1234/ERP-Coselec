from datetime import datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, check_permission
from app.models.user import User
from app.models.employee import Employee
from app.models.hr.hr_request import HRRequest, HRRequestStatus
from app.schemas.hr.hr import HRRequestCreate, HRRequestUpdate, HRRequestResponse
from app.services.request_notifier import notify_request_created, notify_request_status_change

router = APIRouter(prefix="/hr-requests", tags=["HR Requests"])

@router.get("/", response_model=list[HRRequestResponse])
def get_hr_requests(
    _: None = Depends(check_permission("hr_requests.read")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(HRRequest).all()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=HRRequestResponse)
def create_hr_request(
    request_data: HRRequestCreate,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_permission("hr_requests.create")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == request_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    new_request = HRRequest(**request_data.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    background_tasks.add_task(notify_request_created, new_request.id, "HR", ["RH", "Admin"])
    return new_request

@router.put("/{request_id}", response_model=HRRequestResponse)
def update_hr_request(
    request_id: int,
    request_data: HRRequestUpdate,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_permission("hr_requests.update")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.get(HRRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    old_status = request.status
    for key, value in request_data.model_dump(exclude_unset=True).items():
        setattr(request, key, value)

    db.commit()
    db.refresh(request)
    
    if old_status != request.status:
        background_tasks.add_task(notify_request_status_change, request.id, "HR", request.status.value, request.rejection_comment)
        
    return request

@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hr_request(
    request_id: int,
    _: None = Depends(check_permission("hr_requests.delete")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.get(HRRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    db.delete(request)
    db.commit()
    return None
