from pydantic import BaseModel, ConfigDict

from app.models.ticket import (
    TicketCategory,
    TicketStatus
)


class TicketBase(BaseModel):
    title: str
    description: str
    category: TicketCategory
    meta_data: dict | None = None


class TicketCreate(TicketBase):
    pass


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketResponse(TicketBase):
    id: int
    status: TicketStatus
    creator_id: int

    model_config = ConfigDict(
        from_attributes=True
    )
