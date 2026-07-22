from pydantic import BaseModel
from datetime import date
from app.models.project.milestone import MilestoneStatus

class MilestoneBase(BaseModel):
    title: str
    order_index: int = 0
    due_date: date
    status: MilestoneStatus = MilestoneStatus.PENDING

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    achieved_date: date | None = None

    model_config = {
        "from_attributes": True
    }

class MilestoneUpdate(BaseModel):
    title: str | None = None
    order_index: int | None = None
    due_date: date | None = None
    status: MilestoneStatus | None = None
    achieved_date: date | None = None
