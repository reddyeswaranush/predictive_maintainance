from pydantic import BaseModel
from typing import Optional


class IncidentBase(BaseModel):
    machine_id: int
    priority: str
    description: str
    assigned_to: str
    status: str


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    priority: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    status: Optional[str] = None


class IncidentResponse(IncidentBase):
    id: int

    class Config:
        from_attributes = True