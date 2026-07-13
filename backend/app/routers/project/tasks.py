from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import check_permission, get_current_user
from app.schemas.project.task import TaskResponse, TaskUpdate, TaskCreate
from app.models.project.project import Project
from app.models.employee import Employee
from app.models.project.task import Task
router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["tasks"])

#GET
@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
def get_tasks_by_project(project_id:int, db : Session=Depends(get_db), user_permissions=Depends(check_permission("tasks.read"))):
    tasks = (db.query(Task).filter(Task.project_id==project_id).all())
    if len(tasks) ==0:
        raise HTTPException(status_code=status.HTTP_404, detail="Aucune tâche n'a été retrouvée")
    return tasks


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task(task_id: int, db: Session=Depends(get_db), user_permissions=Depends(check_permission("tasks.read"))):
    task = db.query(Task).filter(Task.id==task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tâche non trouvée")
    return task


# POST
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_for_project( task_data : TaskCreate, project_id: int, db: Session=Depends(get_db), user_permissions=Depends(check_permission("tasks.create")), current_user=Depends(get_current_user)):
    existing_task = db.query(Task).filter(Task.project_id==project_id,Task.title == task_data.title).count()
    if existing_task>0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= "Une tâche avec ce titre existe deja dans ce projet")
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projet non trouvé")
    if task_data.assignee_id is not None:
        employee= (db.query(Employee).filter(Employee.id == task_data.assignee_id)).first()
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employé assigné à la tâche non trouvé")
    task_count = db.query(Task).filter(Task.project_id == project_id).count()
    if task_count>100:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Le nombre maximal de tâches par projet a été atteint")
    task = Task(
    **task_data.model_dump(exclude={"project_id"}),
    project_id=project_id,
    author_id=current_user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    return task

#PATCH
@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(project_id: int, task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db), user_permissions=Depends(check_permission("tasks.update"))):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tâche non trouvée dans ce projet")
    
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
        
    db.commit()
    db.refresh(task)
    return task