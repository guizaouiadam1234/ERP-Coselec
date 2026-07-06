# backend/seed_planning.py
import random
from datetime import date, timedelta
from app.database import SessionLocal
from app.models.employee import Employee
from app.models.hr.attendance import Attendance, AttendanceStatus

def seed_attendances():
    db = SessionLocal()
    employees = db.query(Employee).all()
    
    if not employees:
        print("❌ Aucun employé trouvé. Veuillez d'abord ajouter des collaborateurs.")
        db.close()
        return

    # We will generate data from July 1st, 2026 to December 31st, 2026
    # This covers the dates in your screenshot and gives you plenty of padding
    start_date = date(2026, 7, 1)
    end_date = date(2026, 12, 31)
    delta = end_date - start_date
    
    all_dates = [start_date + timedelta(days=i) for i in range(delta.days + 1)]
    
    print("🧹 Nettoyage des anciennes données de présence...")
    db.query(Attendance).delete()
    
    attendances_to_add = []
    
    print("🎲 Génération de données réalistes pour le planning...")
    for emp in employees:
        i = 0
        while i < len(all_dates):
            current_date = all_dates[i]
            
            # Skip weekends (5 = Saturday, 6 = Sunday)
            if current_date.weekday() >= 5:
                i += 1
                continue
                
            # Randomly decide what the employee is doing for this chunk of time
            # Weights: 50% chance of staying on SITE, 40% CHANTIER, 10% CONGE
            state = random.choices(['SITE', 'CHANTIER', 'CONGE'], weights=[50, 40, 10])[0]
            
            # Determine how long they stay in this state to make it look realistic
            if state == 'CHANTIER':
                chunk_size = random.randint(3, 14) # 3 to 14 days on a construction site
            elif state == 'CONGE':
                chunk_size = random.randint(5, 15) # 1 to 3 weeks of vacation
            else:
                chunk_size = random.randint(2, 7) # Standard office days
            
            # Apply the state for the duration of the chunk
            for j in range(chunk_size):
                if i + j < len(all_dates):
                    day = all_dates[i+j]
                    
                    # Only apply to weekdays and ONLY save to DB if it's not the default "SITE"
                    if day.weekday() < 5 and state != 'SITE':
                        record = Attendance(
                            employee_id=emp.id,
                            date=day,
                            status=state
                        )
                        attendances_to_add.append(record)
            
            # Jump forward by the chunk size we just generated
            i += chunk_size
            
    db.add_all(attendances_to_add)
    db.commit()
    db.close()
    
    print(f"✅ Succès ! {len(attendances_to_add)} enregistrements d'affectation ont été ajoutés à la base de données.")

if __name__ == "__main__":
    seed_attendances()