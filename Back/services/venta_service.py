from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.producto import Producto
from models.venta import Venta, TipoVentaEnum, MetodoPagoEnum, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.movimiento import (
    MovimientoInventario,
    TipoMovimientoEnum,
    MotivoMovimientoEnum
)


def crear_venta(
    db: Session,
    productos: list,
    metodo_pago: MetodoPagoEnum
):
    """
    productos = [
        {
            "producto_id": int,
            "cantidad": int,
            "precio_unitario": float
        }
    ]
    """

    try:
        total = 0
        venta_sin_stock = False

        # 1️⃣ Crear venta temporal
        venta = Venta(
            total=0,
            tipo=TipoVentaEnum.normal,
            metodo_pago=metodo_pago,
            estado=EstadoVentaEnum.completa
        )
        db.add(venta)
        db.flush()  # obtenemos venta.id

        # 2️⃣ Procesar productos
        for item in productos:
            producto = db.query(Producto).filter(
                Producto.id == item["producto_id"]
            ).first()

            if not producto:
                raise Exception("Producto no encontrado")

            cantidad = item["cantidad"]
            precio = item["precio_unitario"]

            # 3️⃣ Registrar producto en la venta
            vp = VentaProducto(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio
            )
            db.add(vp)

            # 4️⃣ Movimiento de inventario
            movimiento = MovimientoInventario(
                producto_id=producto.id,
                tipo=TipoMovimientoEnum.salida,
                motivo=MotivoMovimientoEnum.venta,
                cantidad=cantidad,
                referencia_id=venta.id
            )
            db.add(movimiento)

            # 5️⃣ Stock o venta sin stock
            if producto.stock >= cantidad:
                producto.stock -= cantidad
            else:
                venta_sin_stock = True
                producto.ventas_sin_stock += 1

            total += cantidad * precio

        # 6️⃣ Finalizar venta
        venta.total = total
        if venta_sin_stock:
            venta.tipo = TipoVentaEnum.sin_stock

        db.commit()
        return venta

    except SQLAlchemyError as e:
        db.rollback()
        raise e
