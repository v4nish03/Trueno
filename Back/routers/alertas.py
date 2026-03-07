from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.alertas_service import (
    productos_stock_bajo,
    productos_con_ventas_sin_stock,
    productos_por_reponer
)

router = APIRouter()


@router.get("/stock-bajo")
def alerta_stock_bajo(db: Session = Depends(get_db)):
    productos = productos_stock_bajo(db)

    return {
        "total": len(productos),
        "productos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "stock": p.stock,
                "stock_minimo": p.stock_minimo
            }
            for p in productos
        ]
    }


@router.get("/ventas-sin-stock")
def alerta_ventas_sin_stock(db: Session = Depends(get_db)):
    productos = productos_con_ventas_sin_stock(db)

    return {
        "total": len(productos),
        "productos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "ventas_sin_stock": p.ventas_sin_stock
            }
            for p in productos
        ]
    }


@router.get("/productos-por-reponer")
def productos_por_reponer_endpoint(db: Session = Depends(get_db)):
    """
    Vista especial: "Productos por reponer"
    Incluye productos con stock bajo Y con ventas sin stock pendientes
    """
    productos = productos_por_reponer(db)

    return {
        "total": len(productos),
        "productos": [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "stock": p.stock,
                "stock_minimo": p.stock_minimo,
                "ventas_sin_stock": p.ventas_sin_stock,
                "prioridad": "alta" if p.stock == 0 else "media" if p.ventas_sin_stock > 0 else "baja",
                "necesita_reponer": p.stock <= p.stock_minimo or p.ventas_sin_stock > 0
            }
            for p in productos
        ]
    }
