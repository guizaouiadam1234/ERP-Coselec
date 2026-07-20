import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class FacilityRequestStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class FacilityRequestType(str, enum.Enum):
    MAINTENANCE = "Maintenance"
    PURCHASE = "Purchase"
    OTHER = "Other"

class FacilityRequest(Base):
    __tablename__ = "facility_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    request_type = Column(SQLEnum(FacilityRequestType), nullable=False)
    status = Column(SQLEnum(FacilityRequestStatus), default=FacilityRequestStatus.PENDING)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    attachment_id = Column(Integer, nullable=True)
    rejection_comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_facility_requests")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_facility_requests")
    project = relationship("Project")
