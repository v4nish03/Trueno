from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.devolucion import DevolucionRequest, DevolucionResponse
from services.devolucion_service import devolver_producto

router = APIRouter()


@router.post("/{venta_id}/productos", response_model=DevolucionResponse)
def devolver(
    venta_id: int,
    data: DevolucionRequest,
    db: Session = Depends(get_db)
):
    """
    Registra la devolución de un producto de una venta completa.
    - Devuelve el stock al inventario
    - Registra el movimiento de inventario
    - Ajusta el total de la venta
    - La venta sigue siendo trazable en el historial
    """
    try:
        return devolver_producto(
            db,
            venta_id=venta_id,
            producto_id=data.producto_id,
            cantidad_devuelta=data.cantidad
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))