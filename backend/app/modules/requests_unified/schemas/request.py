from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Union, Literal, Annotated
from datetime import date, datetime
from typing import Optional

from app.modules.requests_unified.models.request import (
    RequestType,
    RequestStatus,
    RequestPriority,
)


# ---------------------------------------------------------------------------
# Type-specific payloads (discriminated union on the "type" field)
# ---------------------------------------------------------------------------


class LeavePayload(BaseModel):
    type: Literal["LEAVE"] = "LEAVE"
    employee_id: Optional[int] = None
    start_date: date
    end_date: date
    leave_type: str = "Congé"
    reason: Optional[str] = None


class ITEquipmentPayload(BaseModel):
    type: Literal["IT_EQUIPMENT"] = "IT_EQUIPMENT"
    equipment_type: str  # "laptop", "monitor", "phone", etc.
    specifications: Optional[str] = None
    justification: str


class ITAccessPayload(BaseModel):
    type: Literal["IT_ACCESS"] = "IT_ACCESS"
    system_name: str  # e.g. "VPN", "ERP", "Active Directory"
    access_level: str = "standard"  # "standard", "admin"
    justification: str


class ITIncidentPayload(BaseModel):
    type: Literal["IT_INCIDENT"] = "IT_INCIDENT"
    affected_system: str
    error_message: Optional[str] = None
    impact_level: str = "medium"  # "low", "medium", "high", "critical"
    steps_to_reproduce: Optional[str] = None


class FacilityMaintenancePayload(BaseModel):
    type: Literal["FACILITY_MAINTENANCE"] = "FACILITY_MAINTENANCE"
    location: str
    building: Optional[str] = None
    urgency: str = "routine"  # "routine", "urgent", "emergency"
    description: str


class FacilityBadgePayload(BaseModel):
    type: Literal["FACILITY_BADGE"] = "FACILITY_BADGE"
    badge_type: str = "access"  # "access", "parking", "visitor"
    target_employee_name: Optional[str] = None
    target_employee_id: Optional[int] = None
    zone: Optional[str] = None


class FacilitySuppliesPayload(BaseModel):
    type: Literal["FACILITY_SUPPLIES"] = "FACILITY_SUPPLIES"
    item_description: str
    quantity: int = Field(gt=0, default=1)
    urgency: str = "routine"


class FuelPayload(BaseModel):
    type: Literal["FUEL"] = "FUEL"
    employee_id: Optional[int] = None
    vehicle_plate: str
    destination: str
    fuel_quantity: float = Field(gt=0)
    trip_days: int = Field(gt=0)
    odometer_reading: int = Field(gt=0)
    trip_purpose: str = ""
    affaire_no: Optional[str] = None
    dossier_no: Optional[str] = None


class DocumentPayload(BaseModel):
    type: Literal["DOCUMENT"] = "DOCUMENT"
    document_type: str  # e.g. "attestation_travail", "fiche_paie", "certificat"
    employee_id: Optional[int] = None
    notes: Optional[str] = None


class GenericPayload(BaseModel):
    """Catch-all payload for the OTHER request type."""
    type: Literal["OTHER"] = "OTHER"
    details: Optional[str] = None


# Discriminated union — Pydantic will auto-select the right model based on `payload.type`
RequestPayload = Annotated[
    Union[
        LeavePayload,
        ITEquipmentPayload,
        ITAccessPayload,
        ITIncidentPayload,
        FacilityMaintenancePayload,
        FacilityBadgePayload,
        FacilitySuppliesPayload,
        FuelPayload,
        DocumentPayload,
        GenericPayload,
    ],
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Request CRUD schemas
# ---------------------------------------------------------------------------


class RequestBase(BaseModel):
    description: Optional[str] = None
    project_id: Optional[int] = None


class RequestCreate(RequestBase):
    type: RequestType
    priority: RequestPriority = RequestPriority.NORMAL
    category: Optional[str] = None
    payload: RequestPayload


class RequestUpdateStatus(BaseModel):
    status: RequestStatus
    rejection_comment: Optional[str] = None


class RequestHistoryResponse(BaseModel):
    id: int
    old_status: Optional[str] = None
    new_status: str
    changed_by_id: int
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RequestResponse(RequestBase):
    id: int
    type: RequestType
    status: RequestStatus
    priority: RequestPriority
    category: Optional[str] = None
    requester_id: int
    validator_id: Optional[int] = None
    department_id: Optional[int] = None
    rejection_comment: Optional[str] = None
    payload: dict  # Return as raw dict so any payload type works
    attachment_url: Optional[str] = None
    sla_deadline: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    manager_validator_id: Optional[int] = None
    manager_validated_at: Optional[datetime] = None
    finance_validator_id: Optional[int] = None
    finance_validated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    history: list[RequestHistoryResponse] = []

    class Config:
        from_attributes = True
