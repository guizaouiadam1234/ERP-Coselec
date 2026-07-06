from pydantic import BaseModel
from datetime import date
from typing import Optional

class AttendanceUpdate(BaseModel):
    employee_id: int
    date: date
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True