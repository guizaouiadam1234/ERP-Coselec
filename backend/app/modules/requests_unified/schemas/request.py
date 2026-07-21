from pydantic import BaseModel, Field
from typing import Union, Literal
from datetime import date, datetime
from app.modules.requests_unified.models.request import RequestType, RequestStatus
from typing import Optional

class LeavePayload(BaseModel):
    employee_id: Optional[int] = None
    start_date: date
    end_date: date
    leave_type: str = "Congé"
    reason: Optional[str] = None

class RequestBase(BaseModel):
    description: Optional[str] = None
    project_id: Optional[int] = None

# For creating a new request
class RequestCreate(RequestBase):
    type: RequestType
    # For now, we only support LeavePayload. In the future, we can add DocumentPayload, etc.
    payload: LeavePayload

class RequestUpdateStatus(BaseModel):
    status: RequestStatus
    rejection_comment: Optional[str] = None

class RequestResponse(RequestBase):
    id: int
    type: RequestType
    status: RequestStatus
    requester_id: int
    validator_id: Optional[int] = None
    rejection_comment: Optional[str] = None
    payload: LeavePayload # Or dict in the future if we have multiple
    attachment_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
