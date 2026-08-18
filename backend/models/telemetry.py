from sqlalchemy import Column, Integer, Float, ForeignKey
from backend.database.connection import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id"))

    temperature = Column(Float)
    pressure = Column(Float)
    vibration = Column(Float)
    voltage = Column(Float)
    current = Column(Float)
    power = Column(Float)
    rpm = Column(Float)
    humidity = Column(Float)
    oil_level = Column(Float)

    health_score = Column(Float)
    failure_probability = Column(Float)