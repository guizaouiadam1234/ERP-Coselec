from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import List, Optional
from app.models.project.project import ProjectStatus
from app.schemas.stock.partner import PartnerResponse

class ProjectBase(BaseModel):
    code: str
    nom: str
    date_debut_estimee: date
    date_fin_estimee: date
    date_fin_prevue: date
    budget_estime: Optional[float] = 0.0

class ProjectCreate(ProjectBase):
    pass 

class ProjectResponse(ProjectBase):
    id: int
    status: ProjectStatus = ProjectStatus.STUDY
    date_debut_reelle: Optional[date] = None
    date_fin_reelle: Optional[date] = None
    budget_engage: Optional[float] = 0.0
    
    partners: List[PartnerResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(BaseModel):
    code: Optional[str] = None
    nom: Optional[str] = None

    date_debut_estimee: Optional[date] = None
    date_fin_estimee: Optional[date] = None
    date_fin_prevue: Optional[date] = None

    status: Optional[ProjectStatus] = None

    date_debut_reelle: Optional[date] = None
    date_fin_reelle: Optional[date] = None

    budget_engage: Optional[float] = None