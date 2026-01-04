# services/venta_service.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.venta import Venta, TipoVentaEnum, MetodoPagoEnum, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.producto import Producto
from models.movimiento import TipoMovimientoEnum, MotivoMovimientoEnum

from services.inventario_service import registrar_movimiento
from services.alertas_service import enviar_alertas_stock, enviar_alertas_ventas_sin_stock


def crear_venta(db: Session, items: list[dict], metodo_pago: MetodoPagoEnum):
    try:
        venta = Venta(
            total=0,
            tipo=TipoVentaEnum.normal,
            metodo_pago=metodo_pago,
            estado=EstadoVentaEnum.completa
        )

        db.add(venta)
        db.flush()

        total = 0
        venta_sin_stock = False

        for item in items:
            producto = db.query(Producto).get(item["producto_id"])

            if not producto:
                raise Exception("Producto no encontrado")

            cantidad = item["cantidad"]
            precio = item["precio"]

            vp = VentaProducto(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio
            )

            db.add(vp)

            registrar_movimiento(
                db=db,
                producto=producto,
                cantidad=cantidad,
                tipo=TipoMovimientoEnum.salida,
                motivo=MotivoMovimientoEnum.venta,
                referencia_id=venta.id
            )

            if producto.stock < 0:
                venta_sin_stock = True

            total += cantidad * precio

        venta.total = total
        venta.tipo = (
            TipoVentaEnum.sin_stock if venta_sin_stock else TipoVentaEnum.normal
        )

        db.commit()
        db.refresh(venta)

        # 🔔 ALERTAS POST-VENTA (NO BLOQUEAN)
        enviar_alertas_stock(db)
        enviar_alertas_ventas_sin_stock(db)

        return venta

    except Exception as e:
        db.rollback()
        raise e
