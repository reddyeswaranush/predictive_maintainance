from sqlalchemy import Column, Integer, String
from backend.database.connection import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(String)
    notification_type = Column(String)
    status = Column(String)