from sqlalchemy import Column, Integer, String
from backend.database.connection import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String)
    quantity = Column(Integer)
    supplier = Column(String)
    status = Column(String)