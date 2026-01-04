# services/producto_service.py
from sqlalchemy.orm import Session
from models.producto import Producto
from services.inventario_service import ingreso_stock
from models.movimiento import MotivoMovimientoEnum


def crear_producto(
    db: Session,
    *,
    codigo: str,
    nombre: str,
    precio1: float,
    precio2: float | None = None,
    precio3: float | None = None,
    precio4: float | None = None,
    stock_inicial: int = 0,
    stock_minimo: int = 5,
    ubicacion=None,
    descripcion: str | None = None
):
    producto = Producto(
        codigo=codigo,
        nombre=nombre,
        descripcion=descripcion,
        precio1=precio1,
        precio2=precio2,
        precio3=precio3,
        precio4=precio4,
        stock=0,  # SIEMPRE empieza en 0
        stock_minimo=stock_minimo,
        ubicacion=ubicacion
    )

    db.add(producto)
    db.flush()  # para obtener producto.id

    if stock_inicial > 0:
        ingreso_stock(
            db,
            producto=producto,
            cantidad=stock_inicial,
            motivo=MotivoMovimientoEnum.stock_inicial
        )

    return producto
