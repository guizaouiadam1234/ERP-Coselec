from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class TicketCategory(enum.Enum):
    LEAVE = "Leave"
    PURCHASE = "Purchase"
    FACILITY = "Facility"
    IT = "IT"

class TicketStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)

    # relation créateur
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="created_tickets")

    #métadonnées
    meta_data = Column(JSON, nullable=True)