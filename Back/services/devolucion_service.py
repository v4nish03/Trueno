from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.venta import Venta, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.producto import Producto
from models.movimiento import (
    MovimientoInventario,
    TipoMovimientoEnum,
    MotivoMovimientoEnum
)


def devolver_producto(
    db: Session,
    venta_id: int,
    producto_id: int,
    cantidad_devuelta: int
):
    try:
        venta = db.query(Venta).filter(Venta.id == venta_id).first()
        if not venta:
            raise Exception("Venta no encontrada")

        vp = db.query(VentaProducto).filter(
            VentaProducto.venta_id == venta_id,
            VentaProducto.producto_id == producto_id
        ).first()

        if not vp:
            raise Exception("Producto no pertenece a la venta")

        if cantidad_devuelta > vp.cantidad:
            raise Exception("Cantidad inválida")

        producto = db.query(Producto).filter(
            Producto.id == producto_id
        ).first()

        # 1️⃣ Movimiento de ingreso por devolución
        movimiento = MovimientoInventario(
            producto_id=producto.id,
            tipo=TipoMovimientoEnum.ingreso,
            motivo=MotivoMovimientoEnum.devolucion,
            cantidad=cantidad_devuelta,
            referencia_id=venta.id
        )
        db.add(movimiento)

        # 2️⃣ Ajustar stock
        producto.stock += cantidad_devuelta

        # 3️⃣ Ajustar venta
        descuento = cantidad_devuelta * vp.precio_unitario
        venta.total -= descuento

        # 4️⃣ Ajustar cantidad vendida
        vp.cantidad -= cantidad_devuelta

        # 5️⃣ Estado de venta
        if vp.cantidad == 0:
            venta.estado = EstadoVentaEnum.parcial

        db.commit()
        return venta

    except SQLAlchemyError as e:
        db.rollback()
        raise e
