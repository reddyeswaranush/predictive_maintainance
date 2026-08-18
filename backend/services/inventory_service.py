from sqlalchemy.orm import Session
from backend.models.inventory import Inventory
from backend.schemas.inventory import InventoryCreate, InventoryUpdate


def get_all_inventory(db: Session):
    return db.query(Inventory).all()


def get_inventory_by_id(db: Session, inventory_id: int):
    return db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()


def create_inventory(db: Session, inventory: InventoryCreate):
    db_inventory = Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def update_inventory(db: Session, inventory_id: int, inventory: InventoryUpdate):
    db_inventory = get_inventory_by_id(db, inventory_id)

    if not db_inventory:
        return None

    for key, value in inventory.model_dump(exclude_unset=True).items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)
    return db_inventory


def delete_inventory(db: Session, inventory_id: int):
    db_inventory = get_inventory_by_id(db, inventory_id)

    if not db_inventory:
        return None

    db.delete(db_inventory)
    db.commit()
    return db_inventory