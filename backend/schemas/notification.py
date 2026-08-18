from pydantic import BaseModel
from typing import Optional


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str
    status: str


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    notification_type: Optional[str] = None
    status: Optional[str] = None


class NotificationResponse(NotificationBase):
    id: int

    class Config:
        from_attributes = True