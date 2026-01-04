# services/inventario_service.py

from sqlalchemy.orm import Session
from models.producto import Producto
from models.movimiento import MovimientoInventario, TipoMovimientoEnum, MotivoMovimientoEnum


def registrar_movimiento(
    db: Session,
    producto: Producto,
    cantidad: int,
    tipo: TipoMovimientoEnum,
    motivo: MotivoMovimientoEnum,
    referencia_id: int | None = None
):
    """
    Registra un movimiento y actualiza el stock cacheado.
    """

    movimiento = MovimientoInventario(
        producto_id=producto.id,
        tipo=tipo,
        motivo=motivo,
        cantidad=cantidad,
        referencia_id=referencia_id
    )

    db.add(movimiento)

    # ACTUALIZACIÓN DE STOCK
    if tipo == TipoMovimientoEnum.ingreso:
        producto.stock += cantidad

    elif tipo == TipoMovimientoEnum.salida:
        if producto.stock >= cantidad:
            producto.stock -= cantidad
        else:
            # venta sin stock
            producto.ventas_sin_stock += 1
            producto.stock = producto.stock - cantidad  # queda negativo (deuda)

    elif tipo == TipoMovimientoEnum.ajuste:
        producto.stock = cantidad  # ajuste manual controlado

    db.add(producto)
