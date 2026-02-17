from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


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
    cantidad: int = Field(..., gt=0)
    motivo: Literal["compra", "devolucion", "correccion"] = "compra"
