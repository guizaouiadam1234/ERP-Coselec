from sqlalchemy.orm import Session
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.models.role import Role
from app.models.hr.document import EmployeeDocument
from app.models.employee import Employee
from app.services.email import send_ticket_email
from app.database import SessionLocal
import os

async def notify_request_created(request_id: int, request_category: str, target_role_names: list[str]):
    """
    Called when an employee creates a request.
    Notifies all users holding the target_role_names.
    """
    db: Session = SessionLocal()
    try:
        target_users = db.query(User).join(User.roles).filter(Role.name.in_(target_role_names)).all()
        message = f"Nouvelle demande {request_category} créée : #{request_id}"
        
        for user in target_users:
            db.add(Notification(
                user_id=user.id,
                message=message,
                type=NotificationType.INFO,
                reference_id=request_id
            ))
        db.commit()
    finally:
        db.close()

async def notify_request_status_change(request_id: int, request_category: str, new_status: str, rejection_comment: str | None = None):
    """
    Called when a request status changes.
    Notifies the creator.
    """
    db: Session = SessionLocal()
    try:
        creator_email = None
        creator_id = None
        
        # We need to fetch the request to get creator_id / employee_id
        request_obj = None
        if request_category == "HR":
            from app.models.hr.hr_request import HRRequest
            request_obj = db.get(HRRequest, request_id)
            if request_obj:
                employee = db.query(Employee).filter(Employee.id == request_obj.employee_id).first()
                if employee:
                    creator_email = employee.email
                    # Try to find a user with the same email to send in-app notification
                    user = db.query(User).filter(User.email == employee.email).first()
                    if user:
                        creator_id = user.id
        elif request_category == "Facility":
            from app.models.facility_request import FacilityRequest
            request_obj = db.get(FacilityRequest, request_id)
            if request_obj:
                user = db.query(User).filter(User.id == request_obj.creator_id).first()
                if user:
                    creator_email = user.email
                    creator_id = user.id
        elif request_category == "IT":
            from app.models.it_request import ITRequest
            request_obj = db.get(ITRequest, request_id)
            if request_obj:
                user = db.query(User).filter(User.id == request_obj.creator_id).first()
                if user:
                    creator_email = user.email
                    creator_id = user.id

        if not creator_email and not creator_id:
            return

        # Add DB Notification
        if creator_id:
            message = f"Votre demande {request_category} #{request_id} a changé de statut: {new_status}."
            if rejection_comment:
                message += f" Commentaire: {rejection_comment}"

            db.add(Notification(
                user_id=creator_id,
                message=message,
                type=NotificationType.INFO,
                reference_id=request_id
            ))
            db.commit()

        # Send Email
        if creator_email:
            subject = f"Mise à jour de votre demande {request_category} #{request_id}"
            body = f"<h2>Mise à jour du statut</h2><p>Le statut est maintenant: <b>{new_status}</b>.</p>"
            
            if rejection_comment:
                body += f"<p><b>Commentaire:</b> {rejection_comment}</p>"

            attachments = []
            if new_status in ["Resolved", "Rejected", "Approved", "Closed"]:
                doc_id = None
                if hasattr(request_obj, 'document_id') and request_obj.document_id:
                    doc_id = request_obj.document_id
                elif hasattr(request_obj, 'attachment_id') and request_obj.attachment_id:
                    doc_id = request_obj.attachment_id

                if doc_id:
                    doc = db.query(EmployeeDocument).filter(EmployeeDocument.id == doc_id).first()
                    if doc and doc.storage_path:
                        if os.path.exists(doc.storage_path):
                            attachments.append(doc.storage_path)

            await send_ticket_email(creator_email, subject, body, attachments=attachments)
    finally:
        db.close()
