from sqlalchemy.orm import Session
from models.producto import Producto
from integrations.telegram_bot import enviar_mensaje


def productos_stock_bajo(db: Session):
    return db.query(Producto).filter(
        Producto.stock <= Producto.stock_minimo
    ).all()


def productos_con_ventas_sin_stock(db: Session):
    return db.query(Producto).filter(
        Producto.ventas_sin_stock > 0
    ).all()


def enviar_alertas(db: Session):
    mensajes = []

    productos_bajo_stock = productos_stock_bajo(db)
    if productos_bajo_stock:
        mensajes.append("⚠️ <b>Productos con stock bajo</b>")
        for p in productos_bajo_stock:
            mensajes.append(
                f"• {p.nombre} (stock: {p.stock})"
            )

    productos_sin_stock = productos_con_ventas_sin_stock(db)
    if productos_sin_stock:
        mensajes.append("\n🚨 <b>Ventas sin stock detectadas</b>")
        for p in productos_sin_stock:
            mensajes.append(
                f"• {p.nombre} ({p.ventas_sin_stock} ventas)"
            )

    if mensajes:
        enviar_mensaje("\n".join(mensajes))
