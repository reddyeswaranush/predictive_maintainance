from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database.connection import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id"))

    priority = Column(String)
    description = Column(String)
    assigned_to = Column(String)
    status = Column(String)