from sqlalchemy import Column, Integer, String, Float, ForeignKey
from backend.database.connection import Base


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id"))

    maintenance_type = Column(String)
    technician = Column(String)
    cost = Column(Float)
    remarks = Column(String)
    status = Column(String)