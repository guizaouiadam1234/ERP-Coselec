from sqlalchemy import Column, Integer, String, Date, Table, Float, ForeignKey
import enum
from sqlalchemy.orm import relationship
from app.models.relations import project_partners
from app.database import Base

class ProjectStatus(enum.Enum):
    STUDY = "En etude"
    PLANNED = "Planifié"
    APPROVED = "Approuvé"
    ONGOING = "En cours"
    SUSPENDED = "Suspendu"
    DELAYED = "Retardé"
    BLOCKED = "Bloqué"
    VALIDATION = "En validation"
    FINISHED = "Terminé"
    CLOSED = "Clôturé"
    CANCELED = "Annulé"


class Project(Base):
    __tablename__ = "projects"

    #champs de base
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(10), nullable=False, unique=True)
    nom = Column(String(255), nullable=False)
    
    #champs de dates
    date_debut_estimee = Column(Date, nullable=False)
    date_debut_reelle = Column(Date, nullable=True)
    date_fin_estimee = Column(Date, nullable=False)
    date_fin_prevue = Column(Date, nullable=False)
    date_fin_reelle= Column(Date, nullable=True)

    #champs de coûts
    budget_estime = Column(Float(12,2), default=0.0, nullable=True)
    budget_engage = Column(Float(12,2), default=0.0, nullable=True)

    #relationships
    partners = relationship(
        "Partner", 
        secondary=project_partners, 
        back_populates="projects"
    )
    