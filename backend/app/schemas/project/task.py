from pydantic import BaseModel
from app.models.project.task import TaskPriority, TaskStatus
from datetime import date, datetime


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority
    due_date: date
    start_date: date | None = None  
    assignee_id: int | None = None
    project_id: int | None = None
    milestone_id: int | None = None
    weight: int = 1

class TaskCreate(TaskBase):
    pass

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None

    status: TaskStatus
    priority: TaskPriority

    created_at: datetime
    updated_at: datetime
    due_date: date
    start_date: date | None = None

    author_id: int
    assignee_id: int | None
    project_id: int | None
    milestone_id: int | None = None
    weight: int

    model_config = {
        "from_attributes": True
    }
    
class TaskUpdate(BaseModel):
    title : str | None = None
    description : str | None = None

    status : TaskStatus | None = None
    priority : TaskPriority | None = None

    start_date: date | None = None
    due_date : date | None = None
    assignee_id : int | None = None
    milestone_id : int | None = None
    weight : int | None = None


class TaskDocumentResponse(BaseModel):
    id: int
    task_id: int
    file_name: str
    storage_path: str
    mime_type: str | None = None
    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }

