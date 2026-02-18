from datetime import datetime
from sqlalchemy.orm import Session

from integrations.telegram_bot import enviar_mensaje
from models.producto import Producto
from models.recibo import Recibo
from models.venta import Venta
from models.venta_producto import VentaProducto


def productos_stock_bajo(db: Session):
    return db.query(Producto).filter(
        Producto.stock <= Producto.stock_minimo
    ).all()


def productos_con_ventas_sin_stock(db: Session):
    return db.query(Producto).filter(
        Producto.ventas_sin_stock > 0
    ).all()


def _fmt_fecha(fecha: datetime | str | None) -> str:
    if not fecha:
        return "N/D"
    if isinstance(fecha, str):
        return fecha
    return fecha.strftime("%Y-%m-%d %H:%M:%S")


def enviar_alertas(db: Session):
    """Alerta general (histórica) de estado de inventario."""
    mensajes = []

    productos_bajo_stock = productos_stock_bajo(db)
    if productos_bajo_stock:
        mensajes.append("⚠️ <b>Productos con stock bajo</b>")
        for p in productos_bajo_stock:
            mensajes.append(
                f"• {p.nombre} (stock: {p.stock}, mínimo: {p.stock_minimo})"
            )

    productos_sin_stock = productos_con_ventas_sin_stock(db)
    if productos_sin_stock:
        mensajes.append("\n🚨 <b>Ventas sin stock detectadas (acumulado)</b>")
        for p in productos_sin_stock:
            mensajes.append(
                f"• {p.nombre} ({p.ventas_sin_stock} ventas)"
            )

    if mensajes:
        enviar_mensaje("\n".join(mensajes))


def enviar_alerta_venta_detallada(
    db: Session,
    *,
    venta_id: int,
    recibo_id: int,
    productos_sin_stock_ids: list[int],
):
    """Alerta detallada tras cerrar una venta con incidencias de stock."""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        return False

    recibo = db.query(Recibo).filter(Recibo.id == recibo_id).first()

    items_venta = db.query(VentaProducto).filter(VentaProducto.venta_id == venta_id).all()
    productos_map = {
        p.id: p
        for p in db.query(Producto).filter(Producto.id.in_([i.producto_id for i in items_venta])).all()
    } if items_venta else {}

    lines = [
        "🚨 <b>Venta con incidencia de stock</b>",
        f"• Venta N°: <b>{venta.id}</b>",
        f"• Recibo N°: <b>{recibo.id if recibo else 'N/D'}</b>",
        f"• Fecha venta: <b>{_fmt_fecha(venta.fecha)}</b>",
        f"• Fecha recibo: <b>{_fmt_fecha(recibo.fecha_impresion) if recibo else 'N/D'}</b>",
    ]

    if productos_sin_stock_ids:
        lines.append("\n<b>Productos afectados en esta venta:</b>")
        for vp in items_venta:
            if vp.producto_id in productos_sin_stock_ids:
                p = productos_map.get(vp.producto_id)
                if p:
                    lines.append(
                        f"• {p.nombre} | cant. vendida: {vp.cantidad} | stock actual: {p.stock} | mínimo: {p.stock_minimo}"
                    )

    bajo_stock_relacionado = []
    for vp in items_venta:
        p = productos_map.get(vp.producto_id)
        if p and p.stock <= p.stock_minimo:
            bajo_stock_relacionado.append(p)

    if bajo_stock_relacionado:
        lines.append("\n⚠️ <b>Quedaron en stock bajo tras la venta:</b>")
        vistos = set()
        for p in bajo_stock_relacionado:
            if p.id in vistos:
                continue
            vistos.add(p.id)
            lines.append(f"• {p.nombre} (stock: {p.stock}, mínimo: {p.stock_minimo})")

    return enviar_mensaje("\n".join(lines))
