from sqlalchemy import Column, Integer, String
from backend.database.connection import Base


class Sensor(Base):
    __tablename__ = "sensors"

    sensor_id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)
    location = Column(String)
    status = Column(String)