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


def _enum_value(value):
    """Compatibilidad entre enums y strings persistidos en BD."""
    return value.value if hasattr(value, "value") else value


def _normalizar_metodo_pago(value) -> MetodoPagoEnum:
    """Aceptar metodo de pago en distintos formatos (enum/string/mayúsculas)."""
    if isinstance(value, MetodoPagoEnum):
        return value

    raw = str(value).strip().lower()
    return MetodoPagoEnum(raw)


# ⚠️ IMPORTANTE: rutas estáticas SIEMPRE antes que /{venta_id}
# De lo contrario FastAPI confunde "abrir", "listar", etc. con un ID numérico

@router.get("/")
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Listar ventas con filtros opcionales de fecha"""
    return listar_ventas(db, skip, limit, fecha_desde, fecha_hasta)


@router.post("/abrir")
def abrir_venta(db: Session = Depends(get_db)):
    """
    Crea una nueva venta en estado 'abierta'.
    Luego agrégale productos y ciérrala para completar la transacción.
    """
    try:
        venta = crear_venta_abierta(db)
        return {
            "mensaje": "Venta abierta. Ahora agrega productos y ciérrala.",
            "venta_id": venta.id,
            "estado": venta.estado.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{venta_id}")
def obtener(venta_id: int, db: Session = Depends(get_db)):
    """Obtener todos los detalles de una venta por su ID"""
    try:
        return obtener_venta(db, venta_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{venta_id}/productos")
def agregar_producto(
    venta_id: int,
    data: AgregarProductoVenta,
    db: Session = Depends(get_db)
):
    """
    Agrega un producto a una venta abierta.
    Si el producto ya estaba, suma la cantidad automáticamente.
    """
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
            "precio_unitario": vp.precio_unitario,
            "subtotal": round(vp.cantidad * vp.precio_unitario, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/cerrar")
def cerrar(
    venta_id: int,
    data: CerrarVentaRequest,
    db: Session = Depends(get_db)
):
    """
    Cierra la venta: calcula el total, descuenta stock,
    detecta si hubo ventas sin stock, genera el recibo
    y envía alertas a Telegram si corresponde.
    """
    try:
        cierre_resultado = cerrar_venta(db, venta_id, _normalizar_metodo_pago(data.metodo_pago))

        if isinstance(cierre_resultado, tuple):
            venta, productos_sin_stock_ids = cierre_resultado
        else:
            # Compatibilidad por si cerrar_venta retorna solo venta
            venta = cierre_resultado
            productos_sin_stock_ids = []

        from services.recibo_service import generar_recibo
        recibo = generar_recibo(db, venta.id)

        if _enum_value(venta.tipo) == "sin_stock":
            try:
                from services.alertas_service import enviar_alerta_venta_detallada

                enviar_alerta_venta_detallada(
                    db,
                    venta_id=venta.id,
                    recibo_id=recibo.id,
                    productos_sin_stock_ids=productos_sin_stock_ids,
                )
            except Exception as alert_error:
                # No romper la venta por un problema de notificación
                print(f"Error enviando alerta detallada: {alert_error}")

        return {
            "mensaje": "Venta cerrada exitosamente",
            "venta": {
                "id": venta.id,
                "total": venta.total,
                "tipo": _enum_value(venta.tipo),
                "metodo_pago": _enum_value(venta.metodo_pago),
                "estado": _enum_value(venta.estado),
                "fecha": venta.fecha
            },
            "recibo": {
                "id": recibo.id,
                "codigo_qr": recibo.codigo_qr,
                "fecha_impresion": recibo.fecha_impresion
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{venta_id}/productos/{producto_id}")
def eliminar_producto(
    venta_id: int,
    producto_id: int,
    db: Session = Depends(get_db)
):
    """Eliminar un producto de una venta que todavía está abierta"""
    try:
        return eliminar_producto_venta(db, venta_id, producto_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{venta_id}/anular")
def anular(venta_id: int, db: Session = Depends(get_db)):
    """
    Anula una venta completa.
    Devuelve el stock de todos los productos y registra los movimientos.
    """
    try:
        return anular_venta(db, venta_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
