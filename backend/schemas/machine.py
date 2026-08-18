from pydantic import BaseModel
from typing import Optional

class MachineBase(BaseModel):
    machine_name: str
    department: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = "Running"


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    machine_name: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None


class MachineResponse(MachineBase):
    machine_id: int

    class Config:
        from_attributes = True