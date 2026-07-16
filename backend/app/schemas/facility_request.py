from pydantic import BaseModel, ConfigDict
from app.models.facility_request import FacilityRequestStatus, FacilityRequestType
from datetime import datetime

class FacilityRequestBase(BaseModel):
    title: str
    description: str
    request_type: FacilityRequestType

class FacilityRequestCreate(FacilityRequestBase):
    pass

class FacilityRequestStatusUpdate(BaseModel):
    status: FacilityRequestStatus
    rejection_comment: str | None = None

class FacilityRequestResponse(FacilityRequestBase):
    id: int
    status: FacilityRequestStatus
    creator_id: int
    assigned_to_id: int | None = None
    attachment_id: int | None = None
    rejection_comment: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
