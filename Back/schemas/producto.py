from pydantic import BaseModel
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
    
    class Config:
        from_attributes = True