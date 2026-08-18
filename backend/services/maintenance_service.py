from sqlalchemy.orm import Session
from backend.models.maintenance import Maintenance
from backend.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate


def get_all_maintenances(db: Session):
    return db.query(Maintenance).all()


def get_maintenance_by_id(db: Session, maintenance_id: int):
    return db.query(Maintenance).filter(
        Maintenance.id == maintenance_id
    ).first()


def create_maintenance(db: Session, maintenance: MaintenanceCreate):
    db_maintenance = Maintenance(**maintenance.model_dump())
    db.add(db_maintenance)
    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance


def update_maintenance(db: Session, maintenance_id: int, maintenance: MaintenanceUpdate):
    db_maintenance = get_maintenance_by_id(db, maintenance_id)

    if not db_maintenance:
        return None

    for key, value in maintenance.model_dump(exclude_unset=True).items():
        setattr(db_maintenance, key, value)

    db.commit()
    db.refresh(db_maintenance)
    return db_maintenance


def delete_maintenance(db: Session, maintenance_id: int):
    db_maintenance = get_maintenance_by_id(db, maintenance_id)

    if not db_maintenance:
        return None

    db.delete(db_maintenance)
    db.commit()
    return db_maintenance