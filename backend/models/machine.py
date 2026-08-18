from sqlalchemy import Column, Integer, String
from backend.database.connection import Base


class Machine(Base):
    __tablename__ = "machines"

    machine_id = Column(Integer, primary_key=True, index=True)
    machine_name = Column(String, nullable=False)
    department = Column(String)
    location = Column(String)
    status = Column(String, default="Running")