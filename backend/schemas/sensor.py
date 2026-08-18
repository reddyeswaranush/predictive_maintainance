from pydantic import BaseModel
from typing import Optional


class SensorBase(BaseModel):
    sensor_name: str
    location: Optional[str] = None
    status: Optional[str] = None


class SensorCreate(SensorBase):
    pass


class SensorUpdate(BaseModel):
    sensor_name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None


class SensorResponse(SensorBase):
    sensor_id: int

    class Config:
        from_attributes = True