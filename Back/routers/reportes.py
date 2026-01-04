# routers/reportes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from database import get_db
from services.reportes_service import (
    reporte_ventas_diarias,
    reporte_productos_mas_vendidos,
    reporte_ingresos_inventario,
    reporte_ventas_sin_stock
)

router = APIRouter()


@router.get("/ventas-diarias")
def ventas_diarias(fecha: date, db: Session = Depends(get_db)):
    return reporte_ventas_diarias(db, fecha)


@router.get("/productos-mas-vendidos")
def productos_mas_vendidos(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    return reporte_productos_mas_vendidos(db, fecha_inicio, fecha_fin)


@router.get("/ingresos-inventario")
def ingresos_inventario(
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    return reporte_ingresos_inventario(db, fecha_inicio, fecha_fin)


@router.get("/ventas-sin-stock")
def ventas_sin_stock(db: Session = Depends(get_db)):
    return reporte_ventas_sin_stock(db)
