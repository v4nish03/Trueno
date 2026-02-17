from sqlalchemy.orm import Session

from models.movimiento import MotivoMovimientoEnum, TipoMovimientoEnum
from models.producto import Producto
from models.venta import EstadoVentaEnum, Venta
from models.venta_producto import VentaProducto
from services.inventario_service import registrar_movimiento


def devolver_producto(
    db: Session,
    venta_id: int,
    producto_id: int,
    cantidad_devuelta: int,
):
    try:
        venta = db.query(Venta).filter(Venta.id == venta_id).with_for_update().first()
        if not venta:
            raise Exception("Venta no encontrada")

        if venta.estado == EstadoVentaEnum.anulada:
            raise Exception("No se puede devolver productos de una venta anulada")

        if venta.estado != EstadoVentaEnum.completa:
            raise Exception("Solo se pueden hacer devoluciones de ventas completas")

        vp = (
            db.query(VentaProducto)
            .filter(VentaProducto.venta_id == venta_id, VentaProducto.producto_id == producto_id)
            .with_for_update()
            .first()
        )
        if not vp:
            raise Exception("El producto no pertenece a esta venta")

        if cantidad_devuelta <= 0:
            raise Exception("La cantidad a devolver debe ser mayor a 0")

        if cantidad_devuelta > vp.cantidad:
            raise Exception(f"Cantidad inválida. Solo se vendieron {vp.cantidad} unidades")

        producto = db.query(Producto).filter(Producto.id == producto_id).with_for_update().first()
        if not producto:
            raise Exception("Producto no encontrado")

        registrar_movimiento(
            db,
            producto_id=producto.id,
            tipo=TipoMovimientoEnum.ingreso,
            motivo=MotivoMovimientoEnum.devolucion,
            cantidad=cantidad_devuelta,
            referencia_id=venta.id,
        )

        producto.stock += cantidad_devuelta

        descuento = cantidad_devuelta * vp.precio_unitario
        venta.total = round((venta.total or 0) - descuento, 2)

        if cantidad_devuelta == vp.cantidad:
            db.delete(vp)
        else:
            vp.cantidad -= cantidad_devuelta

        db.commit()
        db.refresh(venta)

        return {
            "mensaje": "Devolución registrada correctamente",
            "venta_id": venta.id,
            "producto_id": producto.id,
            "cantidad_devuelta": cantidad_devuelta,
            "monto_devuelto": round(descuento, 2),
            "nuevo_total_venta": venta.total,
            "stock_actual_producto": producto.stock,
        }

    except Exception:
        db.rollback()
        raise
