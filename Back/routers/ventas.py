from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.venta_service import (
    crear_venta_abierta,
    agregar_producto_a_venta,
    cerrar_venta
)

router = APIRouter()

@router.post("/abrir")
def abrir_venta(db: Session = Depends(get_db)):
    """Crea una nueva venta abierta"""
    return crear_venta_abierta(db)

@router.post("/{venta_id}/productos")
def agregar_producto(
    venta_id: int,
    producto_id: int,
    cantidad: int,
    precio: float,
    db: Session = Depends(get_db)
):
    """Agrega un producto a la venta abierta"""
    return agregar_producto_a_venta(
        db, venta_id, producto_id, cantidad, precio
    )

@router.post("/{venta_id}/cerrar")
def cerrar(
    venta_id: int,
    metodo_pago: str,
    db: Session = Depends(get_db)
):
    """Cierra la venta y genera el recibo"""
    from models.venta import MetodoPagoEnum
    venta = cerrar_venta(db, venta_id, MetodoPagoEnum(metodo_pago))
    
    # Generar recibo
    from services.recibo_service import generar_recibo
    recibo = generar_recibo(db, venta.id)
    
    return {
        "venta": venta,
        "recibo": recibo
    }