import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database import Base

class DocumentCategory(str, enum.Enum):
    IDENTITY = "Identité"
    SOCIAL = "Social/Familial"
    CONTRACT = "Contrat"


class EmployeeDocument(Base):
    __tablename__ = "employee_documents"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    category = Column(Enum(DocumentCategory), nullable=False)
    file_name = Column(String, nullable=False)
    storage_path = Column(String, nullable=False) 
    mime_type = Column(String)
    
    expiry_date = Column(Date, nullable=True) 
    is_verified = Column(Boolean, default=False) 

    employee = relationship("Employee", back_populates="documents")