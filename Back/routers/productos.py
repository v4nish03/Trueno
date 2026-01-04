from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.producto import ProductoCreate
from services.producto_service import crear_producto

router = APIRouter()

@router.post("/")
def crear(producto: ProductoCreate, db: Session = Depends(get_db)):
    return crear_producto(
        db,
        codigo=producto.codigo,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio1=producto.precio1,
        precio2=producto.precio2,
        precio3=producto.precio3,
        precio4=producto.precio4,
        stock_inicial=producto.stock_inicial,
        stock_minimo=producto.stock_minimo
    )
