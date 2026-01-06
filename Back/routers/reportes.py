from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from services.reportes_service import (
    reporte_ventas_diarias,
    reporte_productos_mas_vendidos,
    reporte_ingresos_inventario,
    reporte_ventas_sin_stock,
    reporte_mensual,
    reporte_por_producto,
    reporte_por_metodo_pago,
    dashboard_resumen
)

router = APIRouter()


@router.get("/ventas-diarias")
def ventas_diarias(fecha: date, db: Session = Depends(get_db)):
    """Reporte de ventas de un día específico"""
    return reporte_ventas_diarias(db, fecha)


@router.get("/productos-mas-vendidos")
def productos_mas_vendidos(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    """Top productos más vendidos en un rango de fechas"""
    return reporte_productos_mas_vendidos(db, fecha_inicio, fecha_fin)


@router.get("/ingresos-inventario")
def ingresos_inventario(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    """Reporte de ingresos de inventario"""
    return reporte_ingresos_inventario(db, fecha_inicio, fecha_fin)


@router.get("/ventas-sin-stock")
def ventas_sin_stock(db: Session = Depends(get_db)):
    """Reporte de productos con ventas sin stock"""
    return reporte_ventas_sin_stock(db)


@router.get("/mensual")
def mensual(
    year: int = Query(..., ge=2020, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    """Reporte mensual consolidado"""
    return reporte_mensual(db, year, month)


@router.get("/por-producto")
def por_producto(db: Session = Depends(get_db)):
    """Reporte de ventas por producto (histórico)"""
    return reporte_por_producto(db)


@router.get("/por-metodo-pago")
def por_metodo_pago(db: Session = Depends(get_db)):
    """Reporte de ventas por método de pago (histórico)"""
    return reporte_por_metodo_pago(db)


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    """Dashboard con resumen general del negocio"""
    return dashboard_resumen(db)