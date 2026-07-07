from datetime import date, timedelta
from app.database import SessionLocal #
from app.models.hr.document import EmployeeDocument
from app.services.notification import create_notification #
from app.models.notification import NotificationType

def check_document_expirations():
    db = SessionLocal() #
    try:
        today = date.today()
        warning_6m = today + timedelta(days=180) # Pastille Orange
        warning_3m = today + timedelta(days=90)  # Pastille Rouge

        expiring_docs = db.query(EmployeeDocument).filter(
            EmployeeDocument.expiry_date <= warning_6m,
            EmployeeDocument.expiry_date > today
        ).all()

        for doc in expiring_docs:
            days_left = (doc.expiry_date - today).days
            urgency = "ROUGE" if days_left <= 90 else "ORANGE"
            
            message = f"[{urgency}] Le document {doc.category.value} de l'employé #{doc.employee_id} expire dans {days_left} jours."
            
            # Cibler l'ID du responsable RH. On suppose user_id=1 pour l'exemple.
            create_notification(
                db=db,
                user_id=1, 
                message=message,
                type=NotificationType.SYSTEM, # À adapter selon tes enums
                reference_id=doc.id #
            )
    finally:
        db.close() #