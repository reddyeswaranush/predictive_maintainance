from pydantic import BaseModel
from typing import Optional


class TelemetryBase(BaseModel):
    machine_id: int
    temperature: float
    pressure: float
    vibration: float
    voltage: float
    current: float
    power: float
    rpm: float
    humidity: float
    oil_level: float
    health_score: float
    failure_probability: float


class TelemetryCreate(TelemetryBase):
    pass


class TelemetryUpdate(BaseModel):
    machine_id: Optional[int] = None
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    vibration: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    power: Optional[float] = None
    rpm: Optional[float] = None
    humidity: Optional[float] = None
    oil_level: Optional[float] = None
    health_score: Optional[float] = None
    failure_probability: Optional[float] = None


class TelemetryResponse(TelemetryBase):
    id: int

    class Config:
        from_attributes = True