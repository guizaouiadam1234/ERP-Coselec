import os
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security.auth import get_current_user, check_permission
from app.modules.users.models.user import User
from app.modules.users.models.employee import Employee
from app.models.hr.document import EmployeeDocument, DocumentCategory
from app.services.storage import save_file_locally
from app.schemas.hr.hr import DocumentResponse

router = APIRouter(
    prefix="/employees",
    tags=["Employee Documents"]
)


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    _: None = Depends(check_permission("documents.read")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(EmployeeDocument).filter(EmployeeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")

    if not os.path.isfile(doc.storage_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    return FileResponse(
        path=doc.storage_path,
        media_type=doc.mime_type or "application/octet-stream",
        filename=doc.file_name,
    )

@router.get("/{employee_id}/documents", response_model=list[DocumentResponse])
def get_employee_documents(
    employee_id: int,
    _: None = Depends(check_permission("documents.read")), # Adapte la permission si besoin
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Vérifier que l'employé existe
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable")

    documents = db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).all()
    return documents

@router.post("/{employee_id}/documents", response_model=DocumentResponse)
def upload_employee_document(
    employee_id: int,
    file: UploadFile = File(...),
    category: DocumentCategory = Form(...),
    expiry_date: Optional[date] = Form(None),
    _: None = Depends(check_permission("documents.create")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Vérifier que l'employé existe
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé introuvable")

    # 2. Générer un nom de fichier unique pour éviter les écrasements
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    unique_filename = f"emp_{employee_id}_{uuid.uuid4().hex[:8]}.{file_extension}"

    # 3. Sauvegarde du fichier via le service de stockage
    try:
        storage_path = save_file_locally(file, unique_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

    # 4. Enregistrer dans la base de données
    new_doc = EmployeeDocument(
        employee_id=employee_id,
        category=category,
        file_name=file.filename, # On garde le nom original pour l'affichage
        storage_path=storage_path, # Le chemin de stockage
        mime_type=file.content_type,
        expiry_date=expiry_date,
        is_verified=False
    )

    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return new_doc

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    _: None = Depends(check_permission("documents.delete")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(EmployeeDocument).filter(EmployeeDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")

    # TODO (Optionnel): Ajouter ici la logique pour supprimer physiquement le fichier de MinIO
    # minio_client.remove_object(BUCKET_NAME, doc.storage_path.split("/")[-1])

    db.delete(doc)
    db.commit()
    return {"message": "Document supprimé"}