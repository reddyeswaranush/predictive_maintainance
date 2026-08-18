from sqlalchemy import Column, Integer, Float, ForeignKey
from backend.database.connection import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id"))

    failure_probability = Column(Float)
    health_score = Column(Float)
    predicted_days = Column(Integer)