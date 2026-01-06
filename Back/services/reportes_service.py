from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from models.venta import Venta, MetodoPagoEnum
from models.venta_producto import VentaProducto
from models.producto import Producto


# 📅 Reporte diario
def reporte_diario(db: Session, fecha: date):
    ventas = db.query(Venta).filter(
        func.date(Venta.fecha) == fecha
    ).all()

    total_ventas = sum(v.total for v in ventas)

    return {
        "fecha": fecha,
        "cantidad_ventas": len(ventas),
        "total_vendido": total_ventas
    }


# 📆 Reporte mensual
def reporte_mensual(db: Session, year: int, month: int):
    ventas = db.query(Venta).filter(
        func.extract("year", Venta.fecha) == year,
        func.extract("month", Venta.fecha) == month
    ).all()

    total_ventas = sum(v.total for v in ventas)

    return {
        "year": year,
        "month": month,
        "cantidad_ventas": len(ventas),
        "total_vendido": total_ventas
    }


# 📦 Reporte por producto
def reporte_por_producto(db: Session):
    resultados = (
        db.query(
            Producto.nombre,
            func.sum(VentaProducto.cantidad).label("cantidad_vendida"),
            func.sum(VentaProducto.cantidad * VentaProducto.precio_unitario).label("total")
        )
        .join(VentaProducto, Producto.id == VentaProducto.producto_id)
        .group_by(Producto.nombre)
        .all()
    )

    return [
        {
            "producto": r[0],
            "cantidad_vendida": r[1],
            "total_vendido": r[2]
        }
        for r in resultados
    ]


# 💰 Reporte por método de pago
def reporte_por_metodo_pago(db: Session):
    resultados = (
        db.query(
            Venta.metodo_pago,
            func.sum(Venta.total).label("total")
        )
        .group_by(Venta.metodo_pago)
        .all()
    )

    return [
        {
            "metodo_pago": r[0].value,
            "total": r[1]
        }
        for r in resultados
    ]
