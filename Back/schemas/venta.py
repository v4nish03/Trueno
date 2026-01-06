from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class VentaItem(BaseModel):
    producto_id: int
    cantidad: int
    precio: float

class VentaCreate(BaseModel):
    items: List[VentaItem]
    metodo_pago: str

class AgregarProductoVenta(BaseModel):
    producto_id: int
    cantidad: int
    precio_unitario: float

class CerrarVentaRequest(BaseModel):
    metodo_pago: str  # "efectivo" o "qr"