from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from services.venta_service import (
    crear_venta_abierta,
    agregar_producto_a_venta,
    cerrar_venta,
    obtener_venta,
    listar_ventas,
    eliminar_producto_venta,
    anular_venta
)
from models.venta import MetodoPagoEnum
from schemas.venta import AgregarProductoVenta, CerrarVentaRequest
from typing import Optional
from datetime import date

router = APIRouter()


@router.post("/abrir")
def abrir_venta(db: Session = Depends(get_db)):
    """Crea una nueva venta abierta"""
    try:
        venta = crear_venta_abierta(db)
        return {
            "mensaje": "Venta abierta creada",
            "venta_id": venta.id,
            "estado": venta.estado.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/productos")
def agregar_producto(
    venta_id: int,
    data: AgregarProductoVenta,
    db: Session = Depends(get_db)
):
    """Agrega un producto a la venta abierta"""
    try:
        vp = agregar_producto_a_venta(
            db, 
            venta_id, 
            data.producto_id, 
            data.cantidad, 
            data.precio_unitario
        )
        return {
            "mensaje": "Producto agregado a la venta",
            "venta_id": venta_id,
            "producto_id": vp.producto_id,
            "cantidad": vp.cantidad,
            "precio_unitario": vp.precio_unitario
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/cerrar")
def cerrar(
    venta_id: int,
    data: CerrarVentaRequest,
    db: Session = Depends(get_db)
):
    """Cierra la venta y genera el recibo"""
    try:
        venta = cerrar_venta(db, venta_id, MetodoPagoEnum(data.metodo_pago))
        
        # Generar recibo
        from services.recibo_service import generar_recibo
        recibo = generar_recibo(db, venta.id)
        
        return {
            "mensaje": "Venta cerrada exitosamente",
            "venta": {
                "id": venta.id,
                "total": venta.total,
                "tipo": venta.tipo.value,
                "metodo_pago": venta.metodo_pago.value,
                "estado": venta.estado.value
            },
            "recibo": {
                "id": recibo.id,
                "codigo_qr": recibo.codigo_qr,
                "fecha_impresion": recibo.fecha_impresion
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{venta_id}")
def obtener(venta_id: int, db: Session = Depends(get_db)):
    """Obtener detalles de una venta"""
    try:
        return obtener_venta(db, venta_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/")
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Listar ventas con filtros"""
    return listar_ventas(db, skip, limit, fecha_desde, fecha_hasta)


@router.delete("/{venta_id}/productos/{producto_id}")
def eliminar_producto(
    venta_id: int,
    producto_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un producto de una venta abierta"""
    try:
        return eliminar_producto_venta(db, venta_id, producto_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/anular")
def anular(venta_id: int, db: Session = Depends(get_db)):
    """Anular una venta completa"""
    try:
        return anular_venta(db, venta_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))