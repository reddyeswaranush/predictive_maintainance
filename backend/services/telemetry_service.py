from sqlalchemy.orm import Session
from backend.models.telemetry import Telemetry
from backend.schemas.telemetry import TelemetryCreate, TelemetryUpdate


def get_all_telemetry(db: Session):
    return db.query(Telemetry).all()


def get_telemetry_by_id(db: Session, telemetry_id: int):
    return db.query(Telemetry).filter(
        Telemetry.id == telemetry_id
    ).first()


def create_telemetry(db: Session, telemetry: TelemetryCreate):
    db_telemetry = Telemetry(**telemetry.model_dump())
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry


def update_telemetry(db: Session, telemetry_id: int, telemetry: TelemetryUpdate):
    db_telemetry = get_telemetry_by_id(db, telemetry_id)

    if not db_telemetry:
        return None

    for key, value in telemetry.model_dump(exclude_unset=True).items():
        setattr(db_telemetry, key, value)

    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry


def delete_telemetry(db: Session, telemetry_id: int):
    db_telemetry = get_telemetry_by_id(db, telemetry_id)

    if not db_telemetry:
        return None

    db.delete(db_telemetry)
    db.commit()
    return db_telemetry