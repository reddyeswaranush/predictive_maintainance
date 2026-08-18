from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.connection import get_db

from backend.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
)

from backend.services.inventory_service import (
    get_all_inventory,
    get_inventory_by_id,
    create_inventory,
    update_inventory,
    delete_inventory,
)

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"]
)


@router.get("/", response_model=list[InventoryResponse])
def read_inventory(db: Session = Depends(get_db)):
    return get_all_inventory(db)


@router.get("/{inventory_id}", response_model=InventoryResponse)
def read_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    item = get_inventory_by_id(db, inventory_id)

    if item is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    return item


@router.post("/", response_model=InventoryResponse)
def add_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db)
):
    return create_inventory(db, inventory)


@router.put("/{inventory_id}", response_model=InventoryResponse)
def edit_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db)
):
    updated = update_inventory(db, inventory_id, inventory)

    if updated is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    return updated


@router.delete("/{inventory_id}")
def remove_inventory(
    inventory_id: int,
    db: Session = Depends(get_db)
):
    deleted = delete_inventory(db, inventory_id)

    if deleted is None:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    return {"message": "Inventory item deleted successfully"}