from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
)

from backend.services.incident_service import (
    get_all_incidents,
    get_incident_by_id,
    create_incident,
    update_incident,
    delete_incident,
)

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"]
)


@router.get("/", response_model=list[IncidentResponse])
def read_incidents(db: Session = Depends(get_db)):
    return get_all_incidents(db)


@router.get("/{incident_id}", response_model=IncidentResponse)
def read_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = get_incident_by_id(db, incident_id)

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.post("/", response_model=IncidentResponse)
def add_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    return create_incident(db, incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
def edit_incident(
    incident_id: int,
    incident: IncidentUpdate,
    db: Session = Depends(get_db)
):
    updated = update_incident(db, incident_id, incident)

    if updated is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return updated


@router.delete("/{incident_id}")
def remove_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_incident(db, incident_id)

    if deleted is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"message": "Incident deleted successfully"}