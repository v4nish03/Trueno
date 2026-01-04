from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas.venta import VentaCreate
from services.venta_service import crear_venta
from models.venta import MetodoPagoEnum

router = APIRouter()

@router.post("/")
def vender(data: VentaCreate, db: Session = Depends(get_db)):
    return crear_venta(
        db,
        items=[item.dict() for item in data.items],
        metodo_pago=MetodoPagoEnum(data.metodo_pago)
    )
