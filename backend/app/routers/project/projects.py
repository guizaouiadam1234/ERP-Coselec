from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.project.project import Project
from app.models.stock.partner import Partner
from app.schemas.project.project import ProjectCreate, ProjectResponse
from app.auth import check_permission
from typing import List

router = APIRouter(prefix="/projects", tags=["projects"])

# POST
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data : ProjectCreate, db: Session= Depends(get_db), user_permissions= Depends(check_permission("projects.create"))):
    existing_project = db.query(Project).filter(Project.code == project_data.code).first()
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un projet avec ce code existe deja"
        )

    db_project = Project(**project_data.model_dump())
    db.add(db_project)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un projet avec ce code existe deja"
        )

    db.refresh(db_project)
    return db_project

@router.post("/{project_id}/partners/{partner_id}", status_code=status.HTTP_201_CREATED)
def add_partner_to_project(project_id : int, partner_id:int, role:str, db:Session = Depends(get_db), user_permissions = Depends(check_permission("projects.update"))):
    project = db.query(Project).filter(Project.id == project_id)
    partner = db.query(Partner).filter(Partner.id == partner_id)

    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    if not partner:
        raise HTTPException(status_code=404, detail="Partenaire non trouvé")
    
    project.partner.add(partner)
    db.commit()


# GET
@router.get("/", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_projects(
    db:Session = Depends(get_db),
    user_permissions = Depends(check_permission("projects.read"))
):
    return db.query(Project).all()
 
