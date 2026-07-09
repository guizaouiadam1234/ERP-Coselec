from fastapi import HTTPException
from app.models.ticket import TicketStatus

# Définition des transitions autorisées (Machine à états)
ALLOWED_TRANSITIONS = {
    TicketStatus.OPEN: [TicketStatus.IN_PROGRESS, TicketStatus.CLOSED],
    TicketStatus.IN_PROGRESS: [TicketStatus.RESOLVED, TicketStatus.CLOSED],
    TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],
    TicketStatus.CLOSED: [TicketStatus.OPEN] # Réouverture possible uniquement
}

def validate_ticket_transition(current: TicketStatus, target: TicketStatus):
    if current == target:
        return # Pas de changement
        
    allowed = ALLOWED_TRANSITIONS.get(current, [])
    
    if target not in allowed:
        raise HTTPException(
            status_code=400, 
            detail=f"Transition impossible du statut {current.value} vers {target.value}."
        )