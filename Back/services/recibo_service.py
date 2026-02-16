import uuid
from sqlalchemy.orm import Session

from models.venta import Venta
from models.recibo import Recibo
from models.venta_producto import VentaProducto
from models.producto import Producto


def generar_recibo(db: Session, venta_id: int) -> Recibo:
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise Exception("Venta no encontrada")

    recibo_existente = db.query(Recibo).filter(
        Recibo.venta_id == venta_id
    ).first()

    if recibo_existente:
        return recibo_existente

    recibo = Recibo(
        venta_id=venta.id,
        codigo_qr=str(uuid.uuid4())
    )

    db.add(recibo)
    db.commit()
    db.refresh(recibo)
    return recibo


def obtener_datos_recibo(db: Session, venta_id: int) -> dict:
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise Exception("Venta no encontrada")

    items = []

    productos = db.query(VentaProducto).filter(
        VentaProducto.venta_id == venta.id
    ).all()

    for vp in productos:
        producto = db.query(Producto).filter(
            Producto.id == vp.producto_id
        ).first()

        items.append({
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "cantidad": vp.cantidad,
            "precio_unitario": vp.precio_unitario,
            "subtotal": vp.cantidad * vp.precio_unitario
        })

    return {
        "venta_id": venta.id,
        "fecha": venta.fecha,
        "total": venta.total,
        "metodo_pago": venta.metodo_pago.value,
        "items": items
    }
