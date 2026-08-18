from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
    MaintenanceResponse,
)

from backend.services.maintenance_service import (
    get_all_maintenances,
    get_maintenance_by_id,
    create_maintenance,
    update_maintenance,
    delete_maintenance,
)

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


@router.get("/", response_model=list[MaintenanceResponse])
def read_maintenances(db: Session = Depends(get_db)):
    return get_all_maintenances(db)


@router.get("/{maintenance_id}", response_model=MaintenanceResponse)
def read_maintenance(maintenance_id: int, db: Session = Depends(get_db)):
    maintenance = get_maintenance_by_id(db, maintenance_id)

    if maintenance is None:
        raise HTTPException(status_code=404, detail="Maintenance not found")

    return maintenance


@router.post("/", response_model=MaintenanceResponse)
def add_maintenance(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db)
):
    return create_maintenance(db, maintenance)


@router.put("/{maintenance_id}", response_model=MaintenanceResponse)
def edit_maintenance(
    maintenance_id: int,
    maintenance: MaintenanceUpdate,
    db: Session = Depends(get_db)
):
    updated = update_maintenance(db, maintenance_id, maintenance)

    if updated is None:
        raise HTTPException(status_code=404, detail="Maintenance not found")

    return updated


@router.delete("/{maintenance_id}")
def remove_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_maintenance(db, maintenance_id)

    if deleted is None:
        raise HTTPException(status_code=404, detail="Maintenance not found")

    return {"message": "Maintenance deleted successfully"}