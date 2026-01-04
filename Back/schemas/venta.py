from pydantic import BaseModel
from typing import List

class VentaItem(BaseModel):
    producto_id: int
    cantidad: int
    precio: float

class VentaCreate(BaseModel):
    items: List[VentaItem]
    metodo_pago: str
