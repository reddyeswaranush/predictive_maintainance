from sqlalchemy.orm import Session
from backend.models.notification import Notification
from backend.schemas.notification import NotificationCreate, NotificationUpdate


def get_all_notifications(db: Session):
    return db.query(Notification).all()


def get_notification_by_id(db: Session, notification_id: int):
    return db.query(Notification).filter(
        Notification.id == notification_id
    ).first()


def create_notification(db: Session, notification: NotificationCreate):
    db_notification = Notification(**notification.model_dump())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(db: Session, notification_id: int, notification: NotificationUpdate):
    db_notification = get_notification_by_id(db, notification_id)

    if not db_notification:
        return None

    for key, value in notification.model_dump(exclude_unset=True).items():
        setattr(db_notification, key, value)

    db.commit()
    db.refresh(db_notification)
    return db_notification


def delete_notification(db: Session, notification_id: int):
    db_notification = get_notification_by_id(db, notification_id)

    if not db_notification:
        return None

    db.delete(db_notification)
    db.commit()
    return db_notification