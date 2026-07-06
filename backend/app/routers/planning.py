from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
import unicodedata
from app.auth import get_current_user
from app.database import get_db
from app.models.employee import Employee
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.user import User
from app.schemas.hr.hr import AttendanceUpdate

router = APIRouter(prefix="/hr", tags=["HR Planning"])


def _normalize_status_token(value: str) -> str:
    stripped = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return stripped.strip().replace("-", "_").replace(" ", "_").upper()


def _parse_attendance_status(value: str) -> AttendanceStatus:
    token = _normalize_status_token(value)

    # Accept both API tokens (CHANTIER/SITE/CONGE) and display labels (Chantier/Site/Congé).
    for status in AttendanceStatus:
        if token == _normalize_status_token(status.name) or token == _normalize_status_token(status.value):
            return status

    if token == "CONGE":
        return AttendanceStatus.CONGE

    raise ValueError(f"Unsupported status: {value}")


def _status_to_frontend_token(value: str) -> str:
    try:
        return _parse_attendance_status(value).name
    except ValueError:
        return "SITE"

# --- Endpoint 1: Fetch the Dynamic Schedule Matrix Grid ---
@router.get("/schedule-matrix")
def get_schedule_matrix(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    days_count: int = Query(7, description="Nombre de jours à afficher dans la matrice"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD.")
    
    date_range = [start + timedelta(days=i) for i in range(days_count)]
    employees = db.query(Employee).all()
    
    # Pre-fetch overrides for the date range to avoid N+1 query performance hits
    end_date = date_range[-1]
    start_dt = datetime.combine(start, time.min)
    end_dt = datetime.combine(end_date, time.max)
    overrides = db.query(Attendance).filter(
        Attendance.date >= start_dt,
        Attendance.date <= end_dt
    ).all()
    
    override_map = {(o.employee_id, o.date.date()): o.status for o in overrides}
    
    response_matrix = []
    
    for emp in employees:
        schedule_days = []
        for current_date in date_range:
            
            # RULE 1: Weekends default to NONE (Off-duty)
            if current_date.weekday() >= 5: 
                current_status = "NONE"
            
            else:
                # RULE 2: Read HR override from DB if it exists, otherwise default strictly to "SITE"
                db_lookup_key = (emp.id, current_date)
                if db_lookup_key in override_map:
                    current_status = _status_to_frontend_token(override_map[db_lookup_key])
                else:
                    current_status = "SITE"

            schedule_days.append(current_status)
            
        response_matrix.append({
            "id": emp.id,
            "name": f"{emp.first_name} {emp.last_name}" if hasattr(emp, 'first_name') else emp.name,
            "role": emp.role if hasattr(emp, 'role') else "Technicien",
            "department_id": emp.department_id if hasattr(emp, 'department_id') else 1,
            "schedule": schedule_days
        })
        
    return response_matrix


# --- Endpoint 2: HR Save / Override a Specific Slot ---
@router.post("/assignment")
def update_attendance_slot(
    payload: AttendanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify the target employee profile exists
    emp_exists = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not emp_exists:
        raise HTTPException(status_code=404, detail="Collaborateur introuvable.")
        
    # Validate the status string matches our exact backend ENUM constraints
    try:
        status_enum = _parse_attendance_status(payload.status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Statut invalide. Choisissez parmi: CHANTIER, SITE, CONGE, TELETRAVAIL")

    # Check if a log entry already exists for this specific employee on this date
    existing_record = db.query(Attendance).filter(
        Attendance.employee_id == payload.employee_id,
        func.date(Attendance.date) == payload.date
    ).first()
    
    if existing_record:
        # If the manager selects "SITE" (which is our base default), we can just delete the override
        if status_enum == AttendanceStatus.SITE:
            db.delete(existing_record)
        else:
            # Update the existing restriction row
            existing_record.status = status_enum.value
            existing_record.notes = payload.notes
    else:
        # Create a brand new restriction row if it's not the default office location
        if status_enum != AttendanceStatus.SITE:
            new_record = Attendance(
                employee_id=payload.employee_id,
                date=datetime.combine(payload.date, time.min),
                status=status_enum.value,
                notes=payload.notes
            )
            db.add(new_record)
            
    db.commit()
    return {"message": "Planning mis à jour avec succès"}