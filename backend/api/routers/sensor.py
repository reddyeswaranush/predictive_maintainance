from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.schemas.sensor import (
    SensorCreate,
    SensorUpdate,
    SensorResponse,
)

from backend.services.sensor_service import (
    get_all_sensors,
    get_sensor_by_id,
    create_sensor,
    update_sensor,
    delete_sensor,
)

router = APIRouter(
    prefix="/sensors",
    tags=["Sensors"]
)


@router.get("/", response_model=list[SensorResponse])
def read_sensors(db: Session = Depends(get_db)):
    return get_all_sensors(db)


@router.get("/{sensor_id}", response_model=SensorResponse)
def read_sensor(sensor_id: int, db: Session = Depends(get_db)):
    sensor = get_sensor_by_id(db, sensor_id)

    if sensor is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor not found"
        )

    return sensor


@router.post("/", response_model=SensorResponse)
def add_sensor(
    sensor: SensorCreate,
    db: Session = Depends(get_db)
):
    return create_sensor(db, sensor)


@router.put("/{sensor_id}", response_model=SensorResponse)
def edit_sensor(
    sensor_id: int,
    sensor: SensorUpdate,
    db: Session = Depends(get_db)
):
    updated = update_sensor(
        db,
        sensor_id,
        sensor
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor not found"
        )

    return updated


@router.delete("/{sensor_id}")
def remove_sensor(
    sensor_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_sensor(
        db,
        sensor_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor not found"
        )

    return {
        "message": "Sensor deleted successfully"
    }