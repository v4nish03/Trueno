from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from database import get_db
from models.movimiento import MovimientoInventario, TipoMovimientoEnum
from models.producto import Producto
from typing import Optional
from datetime import date, datetime

router = APIRouter()


@router.get("/")
def listar_movimientos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    tipo: Optional[str] = None,
    producto_id: Optional[int] = None,
    buscar: Optional[str] = None,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todos los movimientos de inventario con filtros opcionales.
    Incluye nombre y código del producto para evitar N+1 queries.
    """
    q = db.query(MovimientoInventario).join(
        Producto, MovimientoInventario.producto_id == Producto.id
    )

    if tipo:
        try:
            q = q.filter(MovimientoInventario.tipo == TipoMovimientoEnum(tipo))
        except ValueError:
            pass

    if producto_id:
        q = q.filter(MovimientoInventario.producto_id == producto_id)

    if buscar:
        q = q.filter(
            Producto.nombre.ilike(f"%{buscar}%") |
            Producto.codigo.ilike(f"%{buscar}%")
        )

    if fecha_desde:
        q = q.filter(MovimientoInventario.fecha >= datetime.combine(fecha_desde, datetime.min.time()))

    if fecha_hasta:
        q = q.filter(MovimientoInventario.fecha <= datetime.combine(fecha_hasta, datetime.max.time()))

    total = q.count()
    movimientos = q.order_by(desc(MovimientoInventario.fecha)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "movimientos": [
            {
                "id": m.id,
                "producto_id": m.producto_id,
                "nombre_producto": m.producto.nombre,
                "codigo_producto": m.producto.codigo,
                "tipo": m.tipo.value if hasattr(m.tipo, "value") else m.tipo,
                "motivo": m.motivo.value if hasattr(m.motivo, "value") else m.motivo,
                "cantidad": m.cantidad,
                "referencia_id": m.referencia_id,
                "fecha": m.fecha,
            }
            for m in movimientos
        ]
    }
