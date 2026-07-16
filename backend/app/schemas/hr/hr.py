from pydantic import BaseModel, model_validator
from datetime import date
from typing import Optional
from app.models.hr.document import DocumentCategory
from app.models.hr.hr_request import HRRequestType, HRRequestStatus

class AttendanceUpdate(BaseModel):
    employee_id: int
    date: date
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Schémas Contrat --- #
class ContractBase(BaseModel):
    employee_id: int
    contract_type: str
    start_date: date
    end_date: Optional[date] = None
    is_active: Optional[bool] = True

class ContractCreate(ContractBase):
    pass

class ContractUpdate(ContractBase):
    contract_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None

class ContractResponse(ContractBase):
    id: int

    class Config:
        from_attributes = True

# --- Leave Requests --- #
class LeaveRequestBase(BaseModel):
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    pdf_url: Optional[str] = None
    justificatif_url: Optional[str] = None

class LeaveRequestCreate(LeaveRequestBase):
    @model_validator(mode="after")
    def check_dates(self) -> "LeaveRequestCreate":
        if self.start_date > self.end_date:
            raise ValueError("La date de début ne peut pas être postérieure à la date de fin.")
        return self

class LeaveRequestUpdate(BaseModel):
    leave_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = None
    status: Optional[str] = None
    pdf_url: Optional[str] = None
    justificatif_url: Optional[str] = None

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    status: str

    class Config:
        from_attributes = True

# --- Schémas HR Request --- #
class HRRequestBase(BaseModel):
    employee_id: int
    request_type: HRRequestType
    start_date: date
    end_date: date

class HRRequestCreate(HRRequestBase):
    @model_validator(mode="after")
    def check_dates(self) -> "HRRequestCreate":
        if self.start_date > self.end_date:
            raise ValueError("La date de début ne peut pas être postérieure à la date de fin.")
        return self

class HRRequestUpdate(BaseModel):
    request_type: Optional[HRRequestType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[HRRequestStatus] = None
    document_id: Optional[int] = None
    rejection_comment: Optional[str] = None

class HRRequestResponse(HRRequestBase):
    id: int
    status: HRRequestStatus
    document_id: Optional[int] = None
    rejection_comment: Optional[str] = None

    class Config:
        from_attributes = True

# --- Documents --- #
class DocumentResponse(BaseModel):
    id: int
    employee_id: int
    category: DocumentCategory
    file_name: str
    storage_path: str
    mime_type: Optional[str] = None
    numero: Optional[str] = None
    expiry_date: Optional[date] = None
    is_verified: bool

    class Config:
        from_attributes = True

