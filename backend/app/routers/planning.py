# backend/app/routers/planning.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.employee import Employee
# Import your real attendance/assignment model here, for example:
# from app.models.attendance import Attendance 

router = APIRouter(prefix="/hr", tags=["HR Planning"])

@router.get("/schedule-matrix")
def get_schedule_matrix(
    start_date: str = Query(..., description="Date de début au format YYYY-MM-DD"),
    days_count: int = Query(7, description="Nombre de jours à afficher"),
    db: Session = Depends(get_db)
):
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD.")
    
    date_range = [start + timedelta(days=i) for i in range(days_count)]
    employees = db.query(Employee).all()
    response_matrix = []
    
    for emp in employees:
        schedule_days = []
        for current_date in date_range:
            
            # RULE 1: Weekends default to NONE (Off-duty)
            if current_date.weekday() >= 5: 
                current_status = "NONE"
            
            else:
                # RULE 2: Standard weekdays default strictly to "SITE" (Sur Site)
                current_status = "SITE"
                
                # RULE 3: Check if HR has explicitly overridden this day's status
                # Here is your query loop structure targeting your database logs:
                # override = db.query(Attendance).filter(
                #     Attendance.employee_id == emp.id,
                #     Attendance.date == current_date
                # ).first()
                #
                # if override:
                #     current_status = override.status # e.g., "CONGE", "CHANTIER", etc.
                
                # --- Baseline Simulation Rule for Preview (Safe to adjust or remove) ---
                if emp.id % 3 == 0 and current_date.weekday() == 2:
                    current_status = "CONGE"
                elif emp.id % 2 == 0 and current_date.weekday() in [0, 1]:
                    current_status = "CHANTIER"

            schedule_days.append(current_status)
            
        response_matrix.append({
            "id": emp.id,
            "name": f"{emp.first_name} {emp.last_name}" if hasattr(emp, 'first_name') else emp.name,
            "role": emp.role if hasattr(emp, 'role') else "Technicien",
            "department_id": emp.department_id if hasattr(emp, 'department_id') else 1,
            "schedule": schedule_days
        })
        
    return response_matrix