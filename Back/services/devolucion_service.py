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
        # 1️⃣ Validar venta
        venta = db.query(Venta).filter(Venta.id == venta_id).first()
        if not venta:
            raise Exception("Venta no encontrada")

        if venta.estado == EstadoVentaEnum.anulada:
            raise Exception("No se puede devolver productos de una venta anulada")

        if venta.estado != EstadoVentaEnum.completa:
            raise Exception("Solo se pueden hacer devoluciones de ventas completas")

        # 2️⃣ Validar que el producto esté en la venta
        vp = db.query(VentaProducto).filter(
            VentaProducto.venta_id == venta_id,
            VentaProducto.producto_id == producto_id
        ).first()

        if not vp:
            raise Exception("El producto no pertenece a esta venta")

        if cantidad_devuelta <= 0:
            raise Exception("La cantidad a devolver debe ser mayor a 0")

        if cantidad_devuelta > vp.cantidad:
            raise Exception(
                f"Cantidad inválida. Solo se vendieron {vp.cantidad} unidades"
            )

        # 3️⃣ Obtener producto
        producto = db.query(Producto).filter(
            Producto.id == producto_id
        ).first()

        if not producto:
            raise Exception("Producto no encontrado")

        # 4️⃣ Registrar movimiento de ingreso por devolución
        movimiento = MovimientoInventario(
            producto_id=producto.id,
            tipo=TipoMovimientoEnum.ingreso,
            motivo=MotivoMovimientoEnum.devolucion,
            cantidad=cantidad_devuelta,
            referencia_id=venta.id
        )
        db.add(movimiento)

        # 5️⃣ Devolver stock al inventario
        producto.stock += cantidad_devuelta

        # 6️⃣ Ajustar total de la venta
        descuento = cantidad_devuelta * vp.precio_unitario
        venta.total = round((venta.total or 0) - descuento, 2)

        # 7️⃣ Ajustar cantidad en venta_productos
        vp.cantidad -= cantidad_devuelta

        # 8️⃣ La venta sigue como "completa" (devolución parcial no anula)
        # Si se devolvió TODO, igual queda como completa con total ajustado
        # El historial de movimientos tiene la trazabilidad completa

        db.commit()
        db.refresh(venta)

        return {
            "mensaje": "Devolución registrada correctamente",
            "venta_id": venta.id,
            "producto_id": producto.id,
            "cantidad_devuelta": cantidad_devuelta,
            "monto_devuelto": round(descuento, 2),
            "nuevo_total_venta": venta.total,
            "stock_actual_producto": producto.stock
        }

    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Error en base de datos: {str(e)}")