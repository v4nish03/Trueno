# services/inventario_service.py
from sqlalchemy.orm import Session
from models.producto import Producto
from models.movimiento import MovimientoInventario, TipoMovimientoEnum, MotivoMovimientoEnum


def registrar_movimiento(
    db: Session,
    *,
    producto_id: int,
    tipo: TipoMovimientoEnum,
    motivo: MotivoMovimientoEnum,
    cantidad: int,
    referencia_id: int | None = None
):
    movimiento = MovimientoInventario(
        producto_id=producto_id,
        tipo=tipo,
        motivo=motivo,
        cantidad=cantidad,
        referencia_id=referencia_id
    )
    db.add(movimiento)


def ingreso_stock(
    db: Session,
    *,
    producto: Producto,
    cantidad: int,
    motivo: MotivoMovimientoEnum,
    referencia_id: int | None = None
):
    producto.stock += cantidad

    registrar_movimiento(
        db,
        producto_id=producto.id,
        tipo=TipoMovimientoEnum.ingreso,
        motivo=motivo,
        cantidad=cantidad,
        referencia_id=referencia_id
    )


def salida_stock(
    db: Session,
    *,
    producto: Producto,
    cantidad: int,
    referencia_id: int | None = None
):
    if producto.stock >= cantidad:
        producto.stock -= cantidad

        registrar_movimiento(
            db,
            producto_id=producto.id,
            tipo=TipoMovimientoEnum.salida,
            motivo=MotivoMovimientoEnum.venta,
            cantidad=cantidad,
            referencia_id=referencia_id
        )
        return True

    # No hay stock → venta sin stock
    producto.ventas_sin_stock += cantidad
    return False


def ajuste_stock(
    db: Session,
    *,
    producto: Producto,
    cantidad: int,
    motivo: MotivoMovimientoEnum = MotivoMovimientoEnum.correccion
):
    producto.stock = cantidad

    registrar_movimiento(
        db,
        producto_id=producto.id,
        tipo=TipoMovimientoEnum.ajuste,
        motivo=motivo,
        cantidad=cantidad
    )
