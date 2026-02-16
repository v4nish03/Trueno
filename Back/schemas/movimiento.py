from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MovimientoResponse(BaseModel):
    id: int
    producto_id: int
    tipo: str
    motivo: str
    cantidad: int
    fecha: datetime
    referencia_id: Optional[int] = None

    class Config:
        from_attributes = True


class IngresoStockRequest(BaseModel):
    cantidad: int
    motivo: str = "compra"  # compra | devolucion | correccion