import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ITRequestStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class ITRequest(Base):
    __tablename__ = "it_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(SQLEnum(ITRequestStatus), default=ITRequestStatus.PENDING)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    attachment_id = Column(Integer, nullable=True)
    rejection_comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_it_requests")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_it_requests")
