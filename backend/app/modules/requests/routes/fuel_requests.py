import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from sqlalchemy import or_, cast, String

logger = logging.getLogger(__name__)


def _escape_like(value: str) -> str:
    """Escape LIKE-special characters to prevent wildcard injection."""
    return value.replace("%", r"\%").replace("_", r"\_")

from app.core.database.session import get_db
from app.core.security.auth import get_current_user, check_permission
from app.modules.users.models.user import User
from app.modules.users.models.employee import Employee
from app.modules.requests.models.fuel_request import FuelRequest, FuelRequestStatus
from app.modules.requests.schemas.fuel_request import FuelRequestCreate, FuelRequestAction, FuelRequestResponse
from app.services.pdf_generator import generate_dmcar_pdf
from app.services.storage import get_file_url_from_minio

router = APIRouter(prefix="/fuel-requests", tags=["Fuel Requests"])

@router.get("/", response_model=list[FuelRequestResponse])
def list_fuel_requests(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("fuel_requests.read"))
):
    query = db.query(FuelRequest).outerjoin(Employee, FuelRequest.employee_id == Employee.id).filter(FuelRequest.is_deleted == False)

    # Row-level security: non-admin/finance/logistics users see only their own requests
    user_roles = {role.name for role in current_user.roles}
    if not user_roles & {"Admin", "Finance", "Stock / Logistique", "Direction"}:
        query = query.filter(FuelRequest.manager_id == current_user.id)

    if search:
        safe_search = _escape_like(search)
        search_term = _escape_like(search.replace("DA-", ""))
        query = query.filter(
            or_(
                cast(FuelRequest.id, String).ilike(f"%{search_term}%"),
                cast(FuelRequest.affaire_no, String).ilike(f"%{safe_search}%"),
                cast(FuelRequest.dossier_no, String).ilike(f"%{safe_search}%"),
                cast(FuelRequest.request_date, String).ilike(f"%{safe_search}%"),
                Employee.first_name.ilike(f"%{safe_search}%"),
                Employee.last_name.ilike(f"%{safe_search}%")
            )
        )
    requests = query.all()
    # Inject employee_name if available
    for r in requests:
        if r.employee:
            r.employee_name = f"{r.employee.first_name} {r.employee.last_name}"
    return requests

@router.post("/", response_model=FuelRequestResponse)
def create_fuel_request(
    payload: FuelRequestCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("fuel_requests.create"))
):
    new_request = FuelRequest(
        **payload.dict(),
        manager_id=current_user.id,
        status=FuelRequestStatus.PENDING_FINANCE
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    if new_request.employee:
        new_request.employee_name = f"{new_request.employee.first_name} {new_request.employee.last_name}"
    return new_request

@router.delete("/{request_id}")
def delete_fuel_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("fuel_requests.delete"))
):
    req = db.query(FuelRequest).filter(FuelRequest.id == request_id, FuelRequest.is_deleted == False).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Ownership check: only the creator or an Admin can delete
    user_roles = {role.name for role in current_user.roles}
    if req.manager_id != current_user.id and "Admin" not in user_roles:
        raise HTTPException(status_code=403, detail="Not authorized to delete this request")

    req.is_deleted = True
    db.commit()
    return {"message": "Request deleted successfully"}


@router.post("/{request_id}/validate/finance/", response_model=FuelRequestResponse)
def validate_finance(
    request_id: int,
    payload: FuelRequestAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("fuel_requests.validate_finance"))
):
    req = db.query(FuelRequest).filter(FuelRequest.id == request_id, FuelRequest.is_deleted == False).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req.status != FuelRequestStatus.PENDING_FINANCE:
        raise HTTPException(status_code=400, detail="Invalid status for finance validation")

    if payload.action == "APPROVE":
        req.status = FuelRequestStatus.APPROVED
        req.finance_validator_id = current_user.id
        req.finance_validated_at = datetime.utcnow()
        
        # Generate the PDF
        try:
            pdf_url = generate_dmcar_pdf(req)
            if pdf_url:
                req.pdf_url = pdf_url
        except Exception:
            logger.exception("Failed to generate PDF for fuel request %s", request_id)
            
    elif payload.action == "REJECT":
        req.status = FuelRequestStatus.REJECTED
        req.rejection_comment = payload.comment

    db.commit()
    db.refresh(req)
    return req

@router.get("/{request_id}/download-pdf")
def download_fuel_request_pdf(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("fuel_requests.read"))
):
    req = db.query(FuelRequest).filter(FuelRequest.id == request_id, FuelRequest.is_deleted == False).first()
    if not req or not req.pdf_url:
        raise HTTPException(status_code=404, detail="PDF non trouvé")
        
    try:
        url = get_file_url_from_minio(req.pdf_url)
        return RedirectResponse(url)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Erreur lors de la récupération du fichier cloud")
