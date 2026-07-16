from pydantic import BaseModel, ConfigDict
from app.models.it_request import ITRequestStatus
from datetime import datetime

class ITRequestBase(BaseModel):
    title: str
    description: str

class ITRequestCreate(ITRequestBase):
    pass

class ITRequestStatusUpdate(BaseModel):
    status: ITRequestStatus
    rejection_comment: str | None = None

class ITRequestResponse(ITRequestBase):
    id: int
    status: ITRequestStatus
    creator_id: int
    assigned_to_id: int | None = None
    attachment_id: int | None = None
    rejection_comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
