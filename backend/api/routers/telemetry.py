from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.schemas.telemetry import (
    TelemetryCreate,
    TelemetryUpdate,
    TelemetryResponse,
)

from backend.services.telemetry_service import (
    get_all_telemetry,
    get_telemetry_by_id,
    create_telemetry,
    update_telemetry,
    delete_telemetry,
)

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"]
)


@router.get("/", response_model=list[TelemetryResponse])
def read_telemetry(db: Session = Depends(get_db)):
    return get_all_telemetry(db)


@router.get("/{telemetry_id}", response_model=TelemetryResponse)
def read_telemetry_by_id(
    telemetry_id: int,
    db: Session = Depends(get_db)
):
    telemetry = get_telemetry_by_id(db, telemetry_id)

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="Telemetry not found"
        )

    return telemetry


@router.post("/", response_model=TelemetryResponse)
def add_telemetry(
    telemetry: TelemetryCreate,
    db: Session = Depends(get_db)
):
    return create_telemetry(db, telemetry)


@router.put("/{telemetry_id}", response_model=TelemetryResponse)
def edit_telemetry(
    telemetry_id: int,
    telemetry: TelemetryUpdate,
    db: Session = Depends(get_db)
):
    updated = update_telemetry(
        db,
        telemetry_id,
        telemetry
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Telemetry not found"
        )

    return updated


@router.delete("/{telemetry_id}")
def remove_telemetry(
    telemetry_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_telemetry(
        db,
        telemetry_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Telemetry not found"
        )

    return {
        "message": "Telemetry deleted successfully"
    }