from pydantic import BaseModel
from typing import Optional


class PredictionBase(BaseModel):
    machine_id: int
    failure_probability: float
    health_score: float
    predicted_days: int


class PredictionCreate(PredictionBase):
    pass


class PredictionUpdate(BaseModel):
    failure_probability: Optional[float] = None
    health_score: Optional[float] = None
    predicted_days: Optional[int] = None


class PredictionResponse(PredictionBase):
    id: int

    class Config:
        from_attributes = True


class MetroTelemetryInput(BaseModel):
    machine_id: int
    timestamp: str
    TP2: float
    TP3: float
    H1: float
    DV_pressure: float
    Reservoirs: float
    Oil_temperature: float
    Motor_current: float
    COMP: float
    DV_eletric: float
    Towers: float
    MPG: float
    LPS: float
    Pressure_switch: float
    Oil_level: float
    Caudal_impulses: float