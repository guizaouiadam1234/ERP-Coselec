from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models.ticket import Ticket
from app.models.user import User
from app.models.notification import NotificationType
from app.schemas.ticket import (
    TicketCreate,
    TicketResponse
)
from app.services.notification import create_notification

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

@router.post(
    "/",
    status_code=201,
    response_model=TicketResponse
)
def create_ticket(
    ticket: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_ticket = Ticket(
        **ticket.model_dump(),
        creator_id=current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Ticket cree: {new_ticket.title}",
        type=NotificationType.INFO,
        reference_id=new_ticket.id
    )

    return new_ticket

@router.get("/", response_model=list[TicketResponse])
def get_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Ticket).all()