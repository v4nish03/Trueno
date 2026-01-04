from pydantic import BaseModel
from typing import Optional

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
