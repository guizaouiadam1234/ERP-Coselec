from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security.auth import get_current_user, check_permission
from app.modules.users.models.user import User
from app.modules.requests_unified.models.request import GenericRequest, RequestStatus, RequestType
from app.modules.requests_unified.schemas.request import RequestCreate, RequestUpdateStatus, RequestResponse
from app.modules.requests_unified.services.leave_workflow import process_approved_leave

router = APIRouter(prefix="/requests", tags=["Requests Unified"])

@router.get("/", response_model=list[RequestResponse])
def get_requests(
    type: RequestType | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(GenericRequest)
    
    # Si l'utilisateur n'est pas un admin/RH, il ne voit que ses propres requêtes
    # (A adapter selon les rôles exacts de l'application)
    # Pour l'instant, on suppose que check_permission gèrera ça sur les routes spécifiques,
    # mais pour une route unifiée, on filtre si l'user n'a pas un rôle spécifique.
    
    # TODO: Add proper RBAC filtering here if needed.
    # For now, let's just return all requests, or filter by type if provided.
    if type:
        query = query.filter(GenericRequest.type == type)
        
    return query.all()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RequestResponse)
def create_request(
    request_data: RequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # L'utilisateur connecté est le demandeur
    new_request = GenericRequest(
        type=request_data.type,
        requester_id=current_user.id,
        project_id=request_data.project_id,
        description=request_data.description,
        payload=jsonable_encoder(request_data.payload)
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return new_request

@router.patch("/{request_id}/status", response_model=RequestResponse)
def update_request_status(
    request_id: int,
    payload: RequestUpdateStatus,
    background_tasks: BackgroundTasks,
    # On suppose que valider une requête demande une permission spéciale
    current_user: User = Depends(check_permission("requests.validate_hr")),
    db: Session = Depends(get_db)
):
    request = db.get(GenericRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only PENDING requests can be updated")
        
    request.status = payload.status
    request.validator_id = current_user.id
    if payload.rejection_comment:
        request.rejection_comment = payload.rejection_comment
        
    db.commit()
    db.refresh(request)
    
    # --- Workflows Post-Approbation ---
    if request.status == RequestStatus.APPROVED:
        if request.type == RequestType.LEAVE:
            start_date = request.payload.get("start_date")
            end_date = request.payload.get("end_date")
            
            # Conversion string to date si nécessaire (Pydantic serialize en string dans le dict)
            from datetime import date
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
                
            # Exécution de la création des présences
            target_employee_id = request.payload.get("employee_id")
            if not target_employee_id:
                target_employee_id = request.requester_id
            
            background_tasks.add_task(process_approved_leave, db, int(target_employee_id), start_date, end_date)
            
    return request

@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    request = db.get(GenericRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    # Un utilisateur ne peut supprimer que ses propres requêtes (ou un admin)
    if request.requester_id != current_user.id: # TODO: add admin check
        raise HTTPException(status_code=403, detail="Not authorized to delete this request")
        
    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot delete a request that is not PENDING")
        
    db.delete(request)
    db.commit()
    return None
