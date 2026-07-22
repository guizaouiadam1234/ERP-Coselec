import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class MilestoneStatus(str, enum.Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    ACHIEVED = "Achieved"
    DELAYED = "Delayed"

class ProjectMilestone(Base):
    __tablename__ = "project_milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    phase_id = Column(Integer, ForeignKey("project_phases.id", ondelete="CASCADE"), nullable=True)
    
    title = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
    due_date = Column(Date, nullable=False)
    achieved_date = Column(Date, nullable=True)
    
    status = Column(SQLEnum(MilestoneStatus), default=MilestoneStatus.PENDING)

    project = relationship("Project", back_populates="milestones")
    phase = relationship("ProjectPhase", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")
