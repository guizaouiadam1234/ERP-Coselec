from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, check_permission
from app.models.user import User
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.hr.leaverequest import LeaveRequest
from app.models.employee import Employee
from app.models.notification import NotificationType
from app.services.notification import create_notification
from app.schemas.hr.hr import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse

router = APIRouter(
    prefix="/leave-requests",
    tags=["Leave Requests"]
)


def _iter_weekdays(start_date, end_date):
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:
            yield current_date
        current_date += timedelta(days=1)


def _apply_leave_to_attendance(db: Session, employee_id: int, start_date, end_date, reason: str | None = None) -> None:
    for current_date in _iter_weekdays(start_date, end_date):
        attendance_date = datetime.combine(current_date, time.min)
        existing_record = db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.date == attendance_date
        ).first()

        if existing_record:
            existing_record.status = AttendanceStatus.CONGE.value
            existing_record.notes = reason
            continue

        db.add(
            Attendance(
                employee_id=employee_id,
                date=attendance_date,
                status=AttendanceStatus.CONGE.value,
                notes=reason,
            )
        )


def _remove_leave_from_attendance(db: Session, employee_id: int, start_date, end_date) -> None:
    for current_date in _iter_weekdays(start_date, end_date):
        attendance_date = datetime.combine(current_date, time.min)
        existing_record = db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.date == attendance_date,
            Attendance.status == AttendanceStatus.CONGE.value
        ).first()

        if existing_record:
            db.delete(existing_record)

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

    new_request = LeaveRequest(**leave_data.model_dump(exclude={"reason"}))
    new_request.status = "Applique"
    db.add(new_request)
    _apply_leave_to_attendance(
        db,
        employee_id=leave_data.employee_id,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        reason=leave_data.reason,
    )
    db.commit()
    db.refresh(new_request)

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Nouveau congé posé pour {employee.first_name} {employee.last_name}",
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

    for key, value in leave_data.model_dump(exclude_unset=True, exclude={"reason"}).items():
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

    _remove_leave_from_attendance(db, request.employee_id, request.start_date, request.end_date)
    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Congé supprimé pour {request.employee.first_name} {request.employee.last_name} du {request.start_date} au {request.end_date}",
        type=NotificationType.INFO,
        reference_id=request.id
    )
    db.delete(request)
    db.commit()
    return {"message": "Leave request deleted successfully"}