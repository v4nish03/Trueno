from sqlalchemy.orm import Session
from models.venta import Venta, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.producto import Producto
from models.movimiento import TipoMovimientoEnum, MotivoMovimientoEnum
from services.inventario_service import registrar_movimiento

def devolver_producto(
    db: Session,
    venta_id: int,
    producto_id: int,
    cantidad: int
):
    venta = db.query(Venta).get(venta_id)
    vp = (
        db.query(VentaProducto)
        .filter_by(venta_id=venta_id, producto_id=producto_id)
        .first()
    )

    if not venta or not vp:
        raise Exception("Venta o producto inválido")

    if cantidad > vp.cantidad:
        raise Exception("Cantidad inválida")

    producto = db.query(Producto).get(producto_id)

    # Movimiento de ingreso
    registrar_movimiento(
        db=db,
        producto=producto,
        cantidad=cantidad,
        tipo=TipoMovimientoEnum.ingreso,
        motivo=MotivoMovimientoEnum.devolucion,
        referencia_id=venta.id
    )

    # Ajustes
    vp.cantidad -= cantidad
    venta.total -= cantidad * vp.precio_unitario

    venta.estado = EstadoVentaEnum.parcial

    db.commit()
