import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class RequestType(str, enum.Enum):
    LEAVE = "LEAVE"
    # D'autres types pourront être ajoutés plus tard (DOCUMENT, IT, FACILITY)

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class GenericRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(RequestType), nullable=False)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING)
    
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    validator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    description = Column(String, nullable=True)
    rejection_comment = Column(String, nullable=True)
    
    # Payload JSON (ex: {"start_date": "2026-07-21", "end_date": "2026-07-25"})
    payload = Column(JSON, default=dict)
    
    attachment_url = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    validator = relationship("User", foreign_keys=[validator_id])
    project = relationship("Project", foreign_keys=[project_id])
