from pydantic import BaseModel
from typing import Optional


class InventoryBase(BaseModel):
    item_name: str
    quantity: int
    supplier: str
    status: str


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    supplier: Optional[str] = None
    status: Optional[str] = None


class InventoryResponse(InventoryBase):
    id: int

    class Config:
        from_attributes = True