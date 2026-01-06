from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta

from models.venta import Venta, MetodoPagoEnum, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.producto import Producto
from models.movimiento import MovimientoInventario, TipoMovimientoEnum


def reporte_ventas_diarias(db: Session, fecha: date):
    """Reporte de ventas de un día específico"""
    ventas = db.query(Venta).filter(
        and_(
            func.date(Venta.fecha) == fecha,
            Venta.estado == EstadoVentaEnum.completa
        )
    ).all()

    total_ventas = sum(v.total or 0 for v in ventas)
    
    # Ventas por método de pago
    efectivo = sum(v.total or 0 for v in ventas if v.metodo_pago == MetodoPagoEnum.efectivo)
    qr = sum(v.total or 0 for v in ventas if v.metodo_pago == MetodoPagoEnum.qr)

    return {
        "fecha": fecha,
        "cantidad_ventas": len(ventas),
        "total_vendido": round(total_ventas, 2),
        "por_metodo_pago": {
            "efectivo": round(efectivo, 2),
            "qr": round(qr, 2)
        },
        "ventas": [
            {
                "id": v.id,
                "hora": v.fecha.strftime("%H:%M"),
                "total": v.total,
                "metodo_pago": v.metodo_pago.value if v.metodo_pago else None,
                "tipo": v.tipo.value if v.tipo else None
            }
            for v in ventas
        ]
    }


def reporte_productos_mas_vendidos(db: Session, fecha_inicio: date, fecha_fin: date):
    """Top productos más vendidos en un rango de fechas"""
    resultados = (
        db.query(
            Producto.id,
            Producto.codigo,
            Producto.nombre,
            func.sum(VentaProducto.cantidad).label("total_vendido"),
            func.sum(VentaProducto.cantidad * VentaProducto.precio_unitario).label("ingreso_total")
        )
        .join(VentaProducto, Producto.id == VentaProducto.producto_id)
        .join(Venta, VentaProducto.venta_id == Venta.id)
        .filter(
            and_(
                Venta.estado == EstadoVentaEnum.completa,
                func.date(Venta.fecha) >= fecha_inicio,
                func.date(Venta.fecha) <= fecha_fin
            )
        )
        .group_by(Producto.id, Producto.codigo, Producto.nombre)
        .order_by(func.sum(VentaProducto.cantidad).desc())
        .limit(20)
        .all()
    )
    
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "total_productos": len(resultados),
        "productos": [
            {
                "producto_id": r[0],
                "codigo": r[1],
                "nombre": r[2],
                "cantidad_vendida": int(r[3]),
                "ingreso_total": round(float(r[4]), 2)
            }
            for r in resultados
        ]
    }


def reporte_ingresos_inventario(db: Session, fecha_inicio: date, fecha_fin: date):
    """Reporte de ingresos de inventario (compras, ajustes)"""
    ingresos = db.query(MovimientoInventario).filter(
        and_(
            MovimientoInventario.tipo == TipoMovimientoEnum.ingreso,
            func.date(MovimientoInventario.fecha) >= fecha_inicio,
            func.date(MovimientoInventario.fecha) <= fecha_fin
        )
    ).all()
    
    # Agrupar por motivo
    por_motivo = {}
    for ingreso in ingresos:
        motivo = ingreso.motivo.value
        if motivo not in por_motivo:
            por_motivo[motivo] = {
                "cantidad_movimientos": 0,
                "cantidad_total": 0
            }
        por_motivo[motivo]["cantidad_movimientos"] += 1
        por_motivo[motivo]["cantidad_total"] += ingreso.cantidad
    
    return {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "total_ingresos": len(ingresos),
        "cantidad_total_ingresada": sum(m.cantidad for m in ingresos),
        "por_motivo": por_motivo,
        "ingresos": [
            {
                "id": m.id,
                "fecha": m.fecha,
                "producto_id": m.producto_id,
                "cantidad": m.cantidad,
                "motivo": m.motivo.value,
                "referencia_id": m.referencia_id
            }
            for m in ingresos
        ]
    }


def reporte_ventas_sin_stock(db: Session):
    """Reporte de productos con ventas sin stock"""
    productos = db.query(Producto).filter(
        Producto.ventas_sin_stock > 0
    ).all()
    
    total_ventas_sin_stock = sum(p.ventas_sin_stock for p in productos)
    
    return {
        "total_productos_afectados": len(productos),
        "total_ventas_sin_stock": total_ventas_sin_stock,
        "productos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "ventas_sin_stock": p.ventas_sin_stock,
                "stock_actual": p.stock,
                "stock_minimo": p.stock_minimo,
                "ubicacion": p.ubicacion.value
            }
            for p in productos
        ]
    }


def reporte_diario(db: Session, fecha: date):
    """LEGACY - mantener compatibilidad"""
    return reporte_ventas_diarias(db, fecha)


def reporte_mensual(db: Session, year: int, month: int):
    """Reporte mensual consolidado"""
    import calendar
    
    # Obtener primer y último día del mes
    primer_dia = date(year, month, 1)
    ultimo_dia = date(year, month, calendar.monthrange(year, month)[1])
    
    ventas = db.query(Venta).filter(
        and_(
            func.date(Venta.fecha) >= primer_dia,
            func.date(Venta.fecha) <= ultimo_dia,
            Venta.estado == EstadoVentaEnum.completa
        )
    ).all()

    total_ventas = sum(v.total or 0 for v in ventas)
    
    # Por método de pago
    efectivo = sum(v.total or 0 for v in ventas if v.metodo_pago == MetodoPagoEnum.efectivo)
    qr = sum(v.total or 0 for v in ventas if v.metodo_pago == MetodoPagoEnum.qr)

    return {
        "year": year,
        "month": month,
        "periodo": f"{year}-{month:02d}",
        "cantidad_ventas": len(ventas),
        "total_vendido": round(total_ventas, 2),
        "promedio_por_venta": round(total_ventas / len(ventas), 2) if ventas else 0,
        "por_metodo_pago": {
            "efectivo": round(efectivo, 2),
            "qr": round(qr, 2)
        }
    }


def reporte_por_producto(db: Session):
    """Reporte general de ventas por producto (todos los tiempos)"""
    resultados = (
        db.query(
            Producto.id,
            Producto.codigo,
            Producto.nombre,
            func.sum(VentaProducto.cantidad).label("cantidad_vendida"),
            func.sum(VentaProducto.cantidad * VentaProducto.precio_unitario).label("total")
        )
        .join(VentaProducto, Producto.id == VentaProducto.producto_id)
        .join(Venta, VentaProducto.venta_id == Venta.id)
        .filter(Venta.estado == EstadoVentaEnum.completa)
        .group_by(Producto.id, Producto.codigo, Producto.nombre)
        .order_by(func.sum(VentaProducto.cantidad).desc())
        .all()
    )

    return [
        {
            "producto_id": r[0],
            "codigo": r[1],
            "producto": r[2],
            "cantidad_vendida": int(r[3]),
            "total_vendido": round(float(r[4]), 2)
        }
        for r in resultados
    ]


def reporte_por_metodo_pago(db: Session):
    """Reporte de ventas por método de pago (todos los tiempos)"""
    resultados = (
        db.query(
            Venta.metodo_pago,
            func.count(Venta.id).label("cantidad"),
            func.sum(Venta.total).label("total")
        )
        .filter(Venta.estado == EstadoVentaEnum.completa)
        .group_by(Venta.metodo_pago)
        .all()
    )

    return [
        {
            "metodo_pago": r[0].value if r[0] else "no_definido",
            "cantidad_ventas": int(r[1]),
            "total": round(float(r[2] or 0), 2)
        }
        for r in resultados
    ]


def dashboard_resumen(db: Session):
    """Dashboard con resumen general del negocio"""
    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=7)
    hace_30_dias = hoy - timedelta(days=30)
    
    # Ventas de hoy
    ventas_hoy = reporte_ventas_diarias(db, hoy)
    
    # Ventas última semana
    ventas_semana = db.query(Venta).filter(
        and_(
            func.date(Venta.fecha) >= hace_7_dias,
            Venta.estado == EstadoVentaEnum.completa
        )
    ).all()
    
    # Ventas último mes
    ventas_mes = db.query(Venta).filter(
        and_(
            func.date(Venta.fecha) >= hace_30_dias,
            Venta.estado == EstadoVentaEnum.completa
        )
    ).all()
    
    # Productos con stock bajo
    productos_stock_bajo = db.query(Producto).filter(
        and_(
            Producto.stock <= Producto.stock_minimo,
            Producto.activo == True
        )
    ).count()
    
    # Productos con ventas sin stock
    productos_sin_stock = db.query(Producto).filter(
        Producto.ventas_sin_stock > 0
    ).count()
    
    return {
        "hoy": {
            "ventas": ventas_hoy["cantidad_ventas"],
            "total": ventas_hoy["total_vendido"]
        },
        "ultima_semana": {
            "ventas": len(ventas_semana),
            "total": round(sum(v.total or 0 for v in ventas_semana), 2)
        },
        "ultimo_mes": {
            "ventas": len(ventas_mes),
            "total": round(sum(v.total or 0 for v in ventas_mes), 2),
            "promedio_diario": round(sum(v.total or 0 for v in ventas_mes) / 30, 2)
        },
        "alertas": {
            "productos_stock_bajo": productos_stock_bajo,
            "productos_ventas_sin_stock": productos_sin_stock
        }
    }