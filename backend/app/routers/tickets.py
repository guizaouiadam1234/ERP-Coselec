from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, check_permission
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User
from app.models.notification import NotificationType
from app.services.workflow import validate_ticket_transition

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

# POST
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TicketResponse
)
def create_ticket(
    ticket: TicketCreate,
    _: None = Depends(check_permission("tickets.create")),
    current_user: User = Depends(get_current_user), # Requis ici pour récupérer l'ID du créateur
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
        message=f"Ticket créé : {new_ticket.title}",
        type=NotificationType.INFO,
        reference_id=new_ticket.id
    )

    return new_ticket


# GET
@router.get("/", response_model=list[TicketResponse])
def get_tickets(
    _: None = Depends(check_permission("tickets.read")),
    db: Session = Depends(get_db)
):
    # Idéalement, on pourrait filtrer pour masquer les tickets archivés par défaut
    return db.query(Ticket).filter(Ticket.status != TicketStatus.ARCHIVED).all()


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    _: None = Depends(check_permission("tickets.read")),
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticket non trouvé"
        )
    return ticket


# PATCH
@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    payload: TicketStatusUpdate,
    background_tasks: BackgroundTasks,
    _: None = Depends(check_permission("tickets.update")),
    db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket non trouvé"
        )

    # Utilisation de ton service de workflow importé pour valider le changement de statut
    if not validate_ticket_transition(ticket.status, payload.status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transition de statut invalide de {ticket.status.value} vers {payload.status.value}"
        )

    new_status_str = payload.status.value
    ticket.status = payload.status
    
    db.commit()
    db.refresh(ticket)

    # Envoi de l'email en arrière-plan
    if ticket.creator and ticket.creator.email:
        background_tasks.add_task(
            send_ticket_email,
            email_to=ticket.creator.email, 
            subject=f"Mise à jour du ticket : {ticket.title}", 
            body=f"Le statut de votre demande est passé à : {new_status_str}"
        )

    # Note : Si tu as besoin de l'ID de l'utilisateur ayant fait la modif pour la notification,
    # tu peux ré-injecter current_user uniquement dans cet endpoint.
    if ticket.creator_id:
        create_notification(
            db=db,
            user_id=ticket.creator_id,
            message=f"Le ticket n°{ticket.id} est passé au statut : {new_status_str}",
            type=NotificationType.INFO,
            reference_id=ticket.id
        )

    return ticket


# DELETE
@router.delete("/{ticket_id}", status_code=status.HTTP_200_OK)
def delete_ticket(
    ticket_id: int, 
    db: Session = Depends(get_db), 
    _: None = Depends(check_permission("tickets.delete"))
):
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Ticket non trouvé"
        )
    
    ticket.status = TicketStatus.ARCHIVED
    db.commit()
    return {"message": "Ticket archivé avec succès !"}