from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductoCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = None
    precio1: float = Field(..., gt=0)
    precio2: Optional[float] = Field(None, gt=0)
    precio3: Optional[float] = Field(None, gt=0)
    precio4: Optional[float] = Field(None, gt=0)
    stock_inicial: int = Field(0, ge=0)
    stock_minimo: int = Field(5, ge=0)
    ubicacion: Optional[str] = "tienda"


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    descripcion: Optional[str] = None
    precio1: Optional[float] = Field(None, gt=0)
    precio2: Optional[float] = Field(None, gt=0)
    precio3: Optional[float] = Field(None, gt=0)
    precio4: Optional[float] = Field(None, gt=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    ubicacion: Optional[str] = None


class ProductoResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str]
    precio1: float
    precio2: Optional[float]
    precio3: Optional[float]
    precio4: Optional[float]
    stock: int
    stock_minimo: int
    ventas_sin_stock: int
    ubicacion: str
    activo: bool
    fecha_creacion: datetime
    fecha_edicion: datetime

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        data = {
            "id": obj.id,
            "codigo": obj.codigo,
            "nombre": obj.nombre,
            "descripcion": obj.descripcion,
            "precio1": obj.precio1,
            "precio2": obj.precio2,
            "precio3": obj.precio3,
            "precio4": obj.precio4,
            "stock": obj.stock,
            "stock_minimo": obj.stock_minimo,
            "ventas_sin_stock": obj.ventas_sin_stock,
            "ubicacion": obj.ubicacion.value,
            "activo": obj.activo,
            "fecha_creacion": obj.fecha_creacion,
            "fecha_edicion": obj.fecha_edicion,
        }
        return cls(**data)
