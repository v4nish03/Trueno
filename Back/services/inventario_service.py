from sqlalchemy.orm import Session

from models.movimiento import MovimientoInventario, MotivoMovimientoEnum, TipoMovimientoEnum
from models.producto import Producto


def registrar_movimiento(
    db: Session,
    *,
    producto_id: int,
    tipo: TipoMovimientoEnum,
    motivo: MotivoMovimientoEnum,
    cantidad: int,
    referencia_id: int | None = None,
):
    if cantidad <= 0:
        raise Exception("La cantidad del movimiento debe ser mayor a 0")

    movimiento = MovimientoInventario(
        producto_id=producto_id,
        tipo=tipo,
        motivo=motivo,
        cantidad=cantidad,
        referencia_id=referencia_id,
    )
    db.add(movimiento)


def ingreso_stock(
    db: Session,
    *,
    producto: Producto,
    cantidad: int,
    motivo: MotivoMovimientoEnum,
    referencia_id: int | None = None,
):
    if cantidad <= 0:
        raise Exception("La cantidad de ingreso debe ser mayor a 0")

    producto.stock += cantidad

    registrar_movimiento(
        db,
        producto_id=producto.id,
        tipo=TipoMovimientoEnum.ingreso,
        motivo=motivo,
        cantidad=cantidad,
        referencia_id=referencia_id,
    )


def salida_stock(
    db: Session,
    *,
    producto: Producto,
    cantidad: int,
    referencia_id: int | None = None,
):
    if cantidad <= 0:
        raise Exception("La cantidad de salida debe ser mayor a 0")

    if producto.stock >= cantidad:
        producto.stock -= cantidad

        registrar_movimiento(
            db,
            producto_id=producto.id,
            tipo=TipoMovimientoEnum.salida,
            motivo=MotivoMovimientoEnum.venta,
            cantidad=cantidad,
            referencia_id=referencia_id,
        )
        return True

    producto.ventas_sin_stock += cantidad
    registrar_movimiento(
        db,
        producto_id=producto.id,
        tipo=TipoMovimientoEnum.salida,
        motivo=MotivoMovimientoEnum.venta,
        cantidad=cantidad,
        referencia_id=referencia_id,
    )
    return False


def ajuste_stock(
    db: Session,
    *,
    producto: Producto,
    cantidad: int,
    motivo: MotivoMovimientoEnum = MotivoMovimientoEnum.correccion,
):
    if cantidad < 0:
        raise Exception("El stock ajustado no puede ser negativo")

    stock_anterior = producto.stock
    producto.stock = cantidad

    delta = abs(cantidad - stock_anterior)
    if delta == 0:
        return

    registrar_movimiento(
        db,
        producto_id=producto.id,
        tipo=TipoMovimientoEnum.ajuste,
        motivo=motivo,
        cantidad=delta,
    )
