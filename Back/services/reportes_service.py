# services/reportes_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from models.venta import Venta, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.movimiento import MovimientoInventario, MotivoMovimientoEnum
from models.producto import Producto


def reporte_ventas_diarias(db: Session, fecha: date):
    """
    Reporte de ventas de un día
    """
    ventas = (
        db.query(Venta)
        .filter(func.date(Venta.fecha) == fecha)
        .filter(Venta.estado != EstadoVentaEnum.anulada)
        .all()
    )

    total_ventas = sum(v.total for v in ventas)
    cantidad_ventas = len(ventas)

    return {
        "fecha": str(fecha),
        "cantidad_ventas": cantidad_ventas,
        "total_vendido": total_ventas,
    }


def reporte_productos_mas_vendidos(db: Session, fecha_inicio: date, fecha_fin: date):
    """
    Productos más vendidos en un rango
    """
    resultados = (
        db.query(
            Producto.nombre,
            func.sum(VentaProducto.cantidad).label("total_vendido")
        )
        .join(VentaProducto, Producto.id == VentaProducto.producto_id)
        .join(Venta, Venta.id == VentaProducto.venta_id)
        .filter(func.date(Venta.fecha).between(fecha_inicio, fecha_fin))
        .filter(Venta.estado != EstadoVentaEnum.anulada)
        .group_by(Producto.nombre)
        .order_by(func.sum(VentaProducto.cantidad).desc())
        .all()
    )

    return [
        {"producto": r.nombre, "cantidad": r.total_vendido}
        for r in resultados
    ]


def reporte_ingresos_inventario(db: Session, fecha_inicio: date, fecha_fin: date):
    """
    Ingresos por compra o devolución
    """
    movimientos = (
        db.query(MovimientoInventario)
        .filter(MovimientoInventario.motivo.in_([
            MotivoMovimientoEnum.compra,
            MotivoMovimientoEnum.devolucion
        ]))
        .filter(func.date(MovimientoInventario.fecha).between(fecha_inicio, fecha_fin))
        .all()
    )

    return [
        {
            "producto_id": m.producto_id,
            "cantidad": m.cantidad,
            "motivo": m.motivo.value,
            "fecha": m.fecha
        }
        for m in movimientos
    ]


def reporte_ventas_sin_stock(db: Session):
    """
    Productos con ventas sin stock
    """
    productos = (
        db.query(Producto)
        .filter(Producto.ventas_sin_stock > 0)
        .all()
    )

    return [
        {
            "producto": p.nombre,
            "ventas_sin_stock": p.ventas_sin_stock
        }
        for p in productos
    ]
