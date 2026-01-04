from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.alertas_service import (
    productos_stock_bajo,
    productos_con_ventas_sin_stock
)

router = APIRouter()

@router.get("/stock-bajo")
def stock_bajo(db: Session = Depends(get_db)):
    return productos_stock_bajo(db)

@router.get("/ventas-sin-stock")
def ventas_sin_stock(db: Session = Depends(get_db)):
    return productos_con_ventas_sin_stock(db)
