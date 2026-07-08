from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, check_permission
from app.models.user import User
from app.models.hr.leaverequest import LeaveRequest
from app.models.employee import Employee
from app.models.notification import NotificationType
from app.services.notification import create_notification
from app.schemas.hr.hr import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse

router = APIRouter(
    prefix="/leave-requests",
    tags=["Leave Requests"]
)

@router.get("/", response_model=list[LeaveRequestResponse])
def get_leave_requests(
    _: None = Depends(check_permission("leaves.read")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(LeaveRequest).all()

@router.post("/", response_model=LeaveRequestResponse)
def create_leave_request(
    leave_data: LeaveRequestCreate,
    _: None = Depends(check_permission("leaves.create")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = db.query(Employee).filter(Employee.id == leave_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    new_request = LeaveRequest(**leave_data.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Nouvelle demande de congé déposée par {employee.first_name} {employee.last_name}",
        type=NotificationType.INFO,
        reference_id=new_request.id
    )
    return new_request

@router.put("/{request_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    request_id: int,
    leave_data: LeaveRequestUpdate,
    _: None = Depends(check_permission("leaves.update")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    for key, value in leave_data.model_dump(exclude_unset=True).items():
        setattr(request, key, value)

    db.commit()
    db.refresh(request)
    return request

@router.delete("/{request_id}")
def delete_leave_request(
    request_id: int,
    _: None = Depends(check_permission("leaves.delete")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Leave request not found")

    db.delete(request)
    db.commit()
    return {"message": "Leave request deleted successfully"}