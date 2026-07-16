import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base

class HRRequestStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class HRRequestType(str, enum.Enum):
    LEAVE = "Leave"
    DOCUMENT = "Document"
    OTHER = "Other"

class HRRequest(Base):
    __tablename__ = "hr_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    request_type = Column(SQLEnum(HRRequestType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(SQLEnum(HRRequestStatus), default=HRRequestStatus.PENDING)
    document_id = Column(Integer, ForeignKey("employee_documents.id"), nullable=True)

    rejection_comment = Column(String, nullable=True)

    employee = relationship("Employee", back_populates="hr_requests")
