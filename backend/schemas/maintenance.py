from pydantic import BaseModel
from typing import Optional


class MaintenanceBase(BaseModel):
    machine_id: int
    maintenance_type: str
    technician: str
    cost: float
    remarks: str
    status: str


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceUpdate(BaseModel):
    maintenance_type: Optional[str] = None
    technician: Optional[str] = None
    cost: Optional[float] = None
    remarks: Optional[str] = None
    status: Optional[str] = None


class MaintenanceResponse(MaintenanceBase):
    id: int

    class Config:
        from_attributes = True