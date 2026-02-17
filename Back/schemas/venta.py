from typing import List, Literal

from pydantic import BaseModel, Field


class VentaItem(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio: float = Field(..., gt=0)


class VentaCreate(BaseModel):
    items: List[VentaItem] = Field(..., min_length=1)
    metodo_pago: Literal["efectivo", "qr"]


class AgregarProductoVenta(BaseModel):
    producto_id: int = Field(..., gt=0)
    cantidad: int = Field(..., gt=0)
    precio_unitario: float = Field(..., gt=0)


class CerrarVentaRequest(BaseModel):
    metodo_pago: Literal["efectivo", "qr"]
