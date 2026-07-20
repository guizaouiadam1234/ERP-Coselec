import enum
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class PhaseStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    DELAYED = "Delayed"

class ProjectPhase(Base):
    __tablename__ = "project_phases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)
    
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    
    status = Column(SQLEnum(PhaseStatus), default=PhaseStatus.PENDING)
    completion_percent = Column(Float, default=0.0)

    project = relationship("Project", back_populates="phases")
    milestones = relationship("ProjectMilestone", back_populates="phase", cascade="all, delete-orphan")
