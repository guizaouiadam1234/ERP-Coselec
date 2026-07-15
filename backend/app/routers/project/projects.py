from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app.models.project.project import Project, ProjectStatus
from app.models.stock.partner import Partner
from app.schemas.project.project import ProjectCreate, ProjectResponse, ProjectUpdate
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
def add_partner_to_project(
    project_id: int,
    partner_id: int,
    db: Session = Depends(get_db),
    user_permissions=Depends(check_permission("projects.update"))
):

    project = db.query(Project).filter(Project.id == project_id).first()
    partner = db.query(Partner).filter(Partner.id == partner_id).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Projet non trouvé"
        )

    if not partner:
        raise HTTPException(
            status_code=404,
            detail="Partenaire non trouvé"
        )

    project.partners.append(partner)

    db.commit()

    return {
        "message": "Partenaire ajouté au projet"
    }


# GET
@router.get("/", response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_projects(
    db:Session = Depends(get_db),
    user_permissions = Depends(check_permission("projects.read"))
):
    return db.query(Project).all()
 
@router.get("/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project(
    project_id:int,
    db:Session = Depends(get_db),
    user_permissions=Depends(check_permission("projects.read")),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project non trouvé")
    return project


# PATCH
@router.patch("/{project_id}")
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session= Depends(get_db),
    user_permissions = Depends(check_permission("projects.update"))
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")
    for key, value in project_data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


#DELETE
@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(project_id: int, db : Session= Depends(get_db), user_permissions = Depends(check_permission("projects.delete"))):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")
    project.status = ProjectStatus.CANCELLED
    db.commit()
    return {"message" : "Project supprimé"}

@router.delete("/{project_id}/partners/{partner_id}", status_code=status.HTTP_200_OK)
def remove_partner_from_project(
    project_id: int,
    partner_id: int,
    db: Session = Depends(get_db),
    user_permissions = Depends(check_permission("projects.update"))
):
    project = db.query(Project).filter(Project.id == project_id).first()
    partner = db.query(Partner).filter(Partner.id == partner_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    if not partner:
        raise HTTPException(status_code=404, detail="Partenaire non trouvé")

    if partner not in project.partners:
        raise HTTPException(status_code=400, detail="Ce partenaire n'est pas associé à ce projet")

    project.partners.remove(partner)
    db.commit()