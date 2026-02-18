from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from models.producto import Producto
from models.venta import EstadoVentaEnum, MetodoPagoEnum, TipoVentaEnum, Venta
from models.venta_producto import VentaProducto
from services.inventario_service import registrar_movimiento
from models.movimiento import MotivoMovimientoEnum, TipoMovimientoEnum


def crear_venta(db: Session, items: list, metodo_pago: MetodoPagoEnum):
    """
    LEGACY - Crear venta completa de una vez
    items = [{"producto_id": int, "cantidad": int, "precio_unitario": float}]
    """
    try:
        total = 0
        venta_sin_stock = False

        venta = Venta(
            total=0,
            tipo=TipoVentaEnum.normal,
            metodo_pago=metodo_pago,
            estado=EstadoVentaEnum.completa,
        )
        db.add(venta)
        db.flush()

        for item in items:
            producto = (
                db.query(Producto)
                .filter(Producto.id == item["producto_id"])
                .with_for_update()
                .first()
            )

            if not producto:
                raise Exception(f"Producto {item['producto_id']} no encontrado")

            cantidad = item["cantidad"]
            precio = item["precio_unitario"]
            if cantidad <= 0 or precio <= 0:
                raise Exception("Cantidad y precio deben ser mayores a 0")

            vp = VentaProducto(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio,
            )
            db.add(vp)

            if producto.stock >= cantidad:
                producto.stock -= cantidad
            else:
                venta_sin_stock = True
                producto.ventas_sin_stock += cantidad

            registrar_movimiento(
                db,
                producto_id=producto.id,
                tipo=TipoMovimientoEnum.salida,
                motivo=MotivoMovimientoEnum.venta,
                cantidad=cantidad,
                referencia_id=venta.id,
            )

            total += cantidad * precio

        venta.total = round(total, 2)
        if venta_sin_stock:
            venta.tipo = TipoVentaEnum.sin_stock

        db.commit()
        db.refresh(venta)
        return venta

    except Exception:
        db.rollback()
        raise


def crear_venta_abierta(db: Session):
    venta = Venta(estado=EstadoVentaEnum.abierta)
    db.add(venta)
    db.commit()
    db.refresh(venta)
    return venta


def agregar_producto_a_venta(
    db: Session,
    venta_id: int,
    producto_id: int,
    cantidad: int,
    precio_unitario: float,
):
    if cantidad <= 0:
        raise Exception("La cantidad debe ser mayor a 0")
    if precio_unitario <= 0:
        raise Exception("El precio unitario debe ser mayor a 0")

    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise Exception("Venta no encontrada")
    if venta.estado != EstadoVentaEnum.abierta:
        raise Exception("Solo se pueden agregar productos a ventas abiertas")

    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise Exception("Producto no encontrado")
    if not producto.activo:
        raise Exception("El producto está descontinuado")

    vp_existente = (
        db.query(VentaProducto)
        .filter(VentaProducto.venta_id == venta_id, VentaProducto.producto_id == producto_id)
        .first()
    )

    if vp_existente:
        vp_existente.cantidad += cantidad
        db.commit()
        db.refresh(vp_existente)
        return vp_existente

    vp = VentaProducto(
        venta_id=venta.id,
        producto_id=producto.id,
        cantidad=cantidad,
        precio_unitario=precio_unitario,
    )
    db.add(vp)
    db.commit()
    db.refresh(vp)

    return vp


def cerrar_venta(db: Session, venta_id: int, metodo_pago: MetodoPagoEnum):
    try:
        venta = db.query(Venta).filter(Venta.id == venta_id).with_for_update().first()
        if not venta:
            raise Exception("Venta no encontrada")
        if venta.estado != EstadoVentaEnum.abierta:
            raise Exception("La venta ya está cerrada")

        productos_venta = db.query(VentaProducto).filter(VentaProducto.venta_id == venta_id).all()
        if not productos_venta:
            raise Exception("No se puede cerrar una venta sin productos")

        producto_ids = [vp.producto_id for vp in productos_venta]
        productos = (
            db.query(Producto)
            .filter(Producto.id.in_(producto_ids))
            .with_for_update()
            .all()
        )
        productos_map = {p.id: p for p in productos}

        total = 0.0
        venta_sin_stock = False
        sin_stock_producto_ids: list[int] = []

        for vp in productos_venta:
            producto = productos_map.get(vp.producto_id)
            if not producto:
                raise Exception(f"Producto {vp.producto_id} no encontrado")

            if producto.stock >= vp.cantidad:
                producto.stock -= vp.cantidad
            else:
                venta_sin_stock = True
                producto.ventas_sin_stock += vp.cantidad
                sin_stock_producto_ids.append(producto.id)

            registrar_movimiento(
                db,
                producto_id=producto.id,
                tipo=TipoMovimientoEnum.salida,
                motivo=MotivoMovimientoEnum.venta,
                cantidad=vp.cantidad,
                referencia_id=venta.id,
            )

            total += vp.cantidad * vp.precio_unitario

        venta.total = round(total, 2)
        venta.metodo_pago = metodo_pago
        venta.tipo = TipoVentaEnum.sin_stock if venta_sin_stock else TipoVentaEnum.normal
        venta.estado = EstadoVentaEnum.completa

        db.commit()
        db.refresh(venta)

        return venta, sin_stock_producto_ids

    except Exception:
        db.rollback()
        raise


def obtener_venta(db: Session, venta_id: int):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise Exception("Venta no encontrada")

    productos_venta = db.query(VentaProducto).filter(VentaProducto.venta_id == venta_id).all()

    items = []
    for vp in productos_venta:
        producto = db.query(Producto).filter(Producto.id == vp.producto_id).first()
        items.append(
            {
                "producto_id": producto.id,
                "codigo": producto.codigo,
                "nombre": producto.nombre,
                "cantidad": vp.cantidad,
                "precio_unitario": vp.precio_unitario,
                "subtotal": vp.cantidad * vp.precio_unitario,
            }
        )

    return {
        "id": venta.id,
        "fecha": venta.fecha,
        "total": venta.total,
        "tipo": venta.tipo.value if venta.tipo else None,
        "metodo_pago": venta.metodo_pago.value if venta.metodo_pago else None,
        "estado": venta.estado.value,
        "items": items,
    }


def listar_ventas(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    fecha_desde: date = None,
    fecha_hasta: date = None,
):
    query = db.query(Venta)

    if fecha_desde:
        query = query.filter(func.date(Venta.fecha) >= fecha_desde)

    if fecha_hasta:
        query = query.filter(func.date(Venta.fecha) <= fecha_hasta)

    ventas = query.order_by(Venta.fecha.desc()).offset(skip).limit(limit).all()

    return [
        {
            "id": v.id,
            "fecha": v.fecha,
            "total": v.total,
            "tipo": v.tipo.value if v.tipo else None,
            "metodo_pago": v.metodo_pago.value if v.metodo_pago else None,
            "estado": v.estado.value,
        }
        for v in ventas
    ]


def eliminar_producto_venta(db: Session, venta_id: int, producto_id: int):
    venta = db.query(Venta).filter(Venta.id == venta_id).first()

    if not venta:
        raise Exception("Venta no encontrada")

    if venta.estado != EstadoVentaEnum.abierta:
        raise Exception("Solo se pueden eliminar productos de ventas abiertas")

    vp = (
        db.query(VentaProducto)
        .filter(VentaProducto.venta_id == venta_id, VentaProducto.producto_id == producto_id)
        .first()
    )

    if not vp:
        raise Exception("Producto no encontrado en la venta")

    db.delete(vp)
    db.commit()
    return {"mensaje": "Producto eliminado de la venta"}


def anular_venta(db: Session, venta_id: int):
    try:
        venta = db.query(Venta).filter(Venta.id == venta_id).with_for_update().first()

        if not venta:
            raise Exception("Venta no encontrada")

        if venta.estado == EstadoVentaEnum.anulada:
            raise Exception("La venta ya está anulada")

        if venta.estado == EstadoVentaEnum.completa:
            productos_venta = db.query(VentaProducto).filter(VentaProducto.venta_id == venta_id).all()
            producto_ids = [vp.producto_id for vp in productos_venta]
            productos = (
                db.query(Producto)
                .filter(Producto.id.in_(producto_ids))
                .with_for_update()
                .all()
            )
            productos_map = {p.id: p for p in productos}

            for vp in productos_venta:
                producto = productos_map.get(vp.producto_id)
                if not producto:
                    raise Exception(f"Producto {vp.producto_id} no encontrado")

                producto.stock += vp.cantidad

                if venta.tipo == TipoVentaEnum.sin_stock and producto.ventas_sin_stock > 0:
                    producto.ventas_sin_stock = max(producto.ventas_sin_stock - vp.cantidad, 0)

                registrar_movimiento(
                    db,
                    producto_id=producto.id,
                    tipo=TipoMovimientoEnum.ingreso,
                    motivo=MotivoMovimientoEnum.devolucion,
                    cantidad=vp.cantidad,
                    referencia_id=venta.id,
                )

        venta.estado = EstadoVentaEnum.anulada
        db.commit()
        db.refresh(venta)

        return {
            "mensaje": "Venta anulada correctamente",
            "venta_id": venta.id,
            "total_devuelto": venta.total,
        }
    except Exception:
        db.rollback()
        raise
