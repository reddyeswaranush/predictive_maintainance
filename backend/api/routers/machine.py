from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.schemas.machine import (
    MachineCreate,
    MachineUpdate,
    MachineResponse,
)

from backend.services.machine_service import (
    get_all_machines,
    get_machine_by_id,
    create_machine,
    update_machine,
    delete_machine,
    get_machines_by_location,
    count_machines_by_location,
)

router = APIRouter(
    prefix="/machines",
    tags=["Machines"]
)


@router.get("/", response_model=list[MachineResponse])
def read_machines(db: Session = Depends(get_db)):
    return get_all_machines(db)


@router.get("/{machine_id}", response_model=MachineResponse)
def read_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = get_machine_by_id(db, machine_id)

    if machine is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    return machine


@router.post("/", response_model=MachineResponse)
def add_machine(
    machine: MachineCreate,
    db: Session = Depends(get_db)
):
    return create_machine(db, machine)


@router.put("/{machine_id}", response_model=MachineResponse)
def edit_machine(
    machine_id: int,
    machine: MachineUpdate,
    db: Session = Depends(get_db)
):
    updated = update_machine(db, machine_id, machine)

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    return updated


@router.delete("/{machine_id}")
def remove_machine(
    machine_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_machine(db, machine_id)

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )

    return {
        "message": "Machine deleted successfully"
    }


@router.get("/location/{location}")
def machines_by_location(
    location: str,
    db: Session = Depends(get_db)
):
    return get_machines_by_location(db, location)


@router.get("/location/{location}/count/{count}")
def machine_count(
    location: str,
    db: Session = Depends(get_db)
):
    return {
        "location": location,
        "count": count_machines_by_location(db, location)
    }