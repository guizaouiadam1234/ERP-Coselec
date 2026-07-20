from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Date, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database.session import Base

class FuelRequestStatus(str, enum.Enum):
    PENDING_LOGISTICS = "PENDING_LOGISTICS"
    PENDING_FINANCE = "PENDING_FINANCE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class FuelRequest(Base):
    __tablename__ = "fuel_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # Context
    request_date = Column(Date, nullable=False)
    affaire_no = Column(String, index=True, nullable=True)
    dossier_no = Column(String, index=True, nullable=True)
    
    # Trip Details
    objet_deplacement = Column(String, nullable=False)
    vehicule_matricule = Column(String, index=True, nullable=False)
    destination = Column(String, nullable=False)
    releve_kilometrique = Column(Integer, nullable=False)
    nombre_jours = Column(Integer, nullable=False)
    
    # Fuel Details
    quantite_carburant = Column(Numeric(10, 2), nullable=False)
    
    # Storage
    pdf_url = Column(String, nullable=True)
    
    # Status
    status = Column(SQLEnum(FuelRequestStatus), default=FuelRequestStatus.PENDING_FINANCE)
    
    # Signatures Tracker
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    logistics_validator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    logistics_validated_at = Column(DateTime, nullable=True)
    
    finance_validator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    finance_validated_at = Column(DateTime, nullable=True)
    
    rejection_comment = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id])
    manager = relationship("User", foreign_keys=[manager_id])
    logistics_validator = relationship("User", foreign_keys=[logistics_validator_id])
    finance_validator = relationship("User", foreign_keys=[finance_validator_id])
    project = relationship("Project", foreign_keys=[project_id])
