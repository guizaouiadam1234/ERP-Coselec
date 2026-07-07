from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, check_permission
from app.models.ticket import Ticket
from app.models.user import User
from app.models.notification import NotificationType
from fastapi import BackgroundTasks

from app.schemas.ticket import (
    TicketCreate,
    TicketStatusUpdate,
    TicketResponse
)
from app.services.notification import create_notification
from app.services.email import send_ticket_email

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
    _: None = Depends(check_permission("tickets.create")),
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
    _: None = Depends(check_permission("tickets.read")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Ticket).all()


@router.patch(
    "/{ticket_id}/status/",
    response_model=TicketResponse
)
@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    include_in_schema=False
)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_permission("tickets.update")),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = (
        db.query(Ticket)
        .filter(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    ticket.status = payload.status
    db.commit()
    db.refresh(ticket)

    background_tasks.add_task(
        send_ticket_email,
        email_to=ticket.creator.email, 
        subject=f"Mise à jour du ticket: {ticket.title}", 
        body=f"Le statut de votre demande est passé à : {ticket.status.value}"
    )

    create_notification(
        db=db,
        user_id=current_user.id,
        message=f"Ticket {ticket.id} passe a {ticket.status.value}",
        type=NotificationType.INFO,
        reference_id=ticket.id
    )

    return ticket