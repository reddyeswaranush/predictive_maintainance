from sqlalchemy.orm import Session
from backend.models.sensor import Sensor
from backend.schemas.sensor import SensorCreate, SensorUpdate


def get_all_sensors(db: Session):
    return db.query(Sensor).all()


def get_sensor_by_id(db: Session, sensor_id: int):
    return db.query(Sensor).filter(
        Sensor.sensor_id == sensor_id
    ).first()


def create_sensor(db: Session, sensor: SensorCreate):
    db_sensor = Sensor(**sensor.model_dump())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    return db_sensor


def update_sensor(db: Session, sensor_id: int, sensor: SensorUpdate):
    db_sensor = get_sensor_by_id(db, sensor_id)

    if not db_sensor:
        return None

    for key, value in sensor.model_dump(exclude_unset=True).items():
        setattr(db_sensor, key, value)

    db.commit()
    db.refresh(db_sensor)
    return db_sensor


def delete_sensor(db: Session, sensor_id: int):
    db_sensor = get_sensor_by_id(db, sensor_id)

    if not db_sensor:
        return None

    db.delete(db_sensor)
    db.commit()
    return db_sensor