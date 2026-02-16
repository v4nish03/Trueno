from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from services.alertas_service import (
    productos_stock_bajo,
    productos_con_ventas_sin_stock
)

router = APIRouter(
    prefix="/alertas",
    tags=["Alertas"]
)


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
