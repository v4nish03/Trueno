from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProductoCreate(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio1: float
    precio2: Optional[float] = None
    precio3: Optional[float] = None
    precio4: Optional[float] = None
    stock_inicial: int = 0
    stock_minimo: int = 5
    ubicacion: Optional[str] = "tienda"

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio1: Optional[float] = None
    precio2: Optional[float] = None
    precio3: Optional[float] = None
    precio4: Optional[float] = None
    stock_minimo: Optional[int] = None
    ubicacion: Optional[str] = None

# ✅ CORREGIDO - Usar ConfigDict en lugar de class Config
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
    
    # ✅ NUEVO - ConfigDict en lugar de class Config
    model_config = ConfigDict(from_attributes=True)
    
    # ✅ CORREGIDO - from_orm sigue funcionando
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
            "fecha_edicion": obj.fecha_edicion
        }
        return cls(**data)