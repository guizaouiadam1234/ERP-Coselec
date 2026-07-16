from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security.auth import get_current_user, check_permission
from app.models.it_request import ITRequest, ITRequestStatus
from app.modules.users.models.user import User
from app.schemas.it_request import ITRequestCreate, ITRequestStatusUpdate, ITRequestResponse
from app.services.request_notifier import notify_request_created, notify_request_status_change

router = APIRouter(prefix="/it-requests", tags=["IT Requests"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ITRequestResponse)
def create_it_request(
    request: ITRequestCreate,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_permission("it_requests.create")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_request = ITRequest(**request.model_dump(), creator_id=current_user.id)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    background_tasks.add_task(notify_request_created, new_request.id, "IT", ["IT", "Admin"])
    return new_request

@router.get("/", response_model=list[ITRequestResponse])
def get_it_requests(_: None = Depends(check_permission("it_requests.read")), db: Session = Depends(get_db)):
    return db.query(ITRequest).all()

@router.get("/{request_id}", response_model=ITRequestResponse)
def get_it_request(request_id: int, _: None = Depends(check_permission("it_requests.read")), db: Session = Depends(get_db)):
    request = db.get(ITRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request

@router.patch("/{request_id}/status", response_model=ITRequestResponse)
def update_it_request_status(
    request_id: int,
    payload: ITRequestStatusUpdate,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_permission("it_requests.update")),
    db: Session = Depends(get_db)
):
    request = db.get(ITRequest, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    old_status = request.status
    request.status = payload.status
    if payload.rejection_comment is not None:
        request.rejection_comment = payload.rejection_comment
    db.commit()
    db.refresh(request)

    if old_status != payload.status:
        background_tasks.add_task(notify_request_status_change, request.id, "IT", payload.status.value, payload.rejection_comment)
        
    return request
