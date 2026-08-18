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