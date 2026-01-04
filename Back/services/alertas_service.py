# services/alertas_service.py
from sqlalchemy.orm import Session
from models.producto import Producto
from services.telegram_service import enviar_mensaje

# ⚠️ Estos valores luego pueden ir a settings
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI"


def productos_stock_bajo(db: Session):
    """
    Productos con stock <= stock mínimo
    """
    return (
        db.query(Producto)
        .filter(Producto.stock <= Producto.stock_minimo)
        .all()
    )


def productos_con_ventas_sin_stock(db: Session):
    """
    Productos que se vendieron sin stock
    """
    return (
        db.query(Producto)
        .filter(Producto.ventas_sin_stock > 0)
        .all()
    )


def enviar_alertas_stock(db: Session):
    productos = productos_stock_bajo(db)

    if not productos:
        return

    mensaje = "⚠️ *ALERTA DE STOCK BAJO*\n\n"

    for p in productos:
        mensaje += f"- {p.nombre} | Stock: {p.stock}\n"

    enviar_mensaje(
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
        mensaje
    )


def enviar_alertas_ventas_sin_stock(db: Session):
    productos = productos_con_ventas_sin_stock(db)

    if not productos:
        return

    mensaje = "🚨 *VENTAS SIN STOCK DETECTADAS*\n\n"

    for p in productos:
        mensaje += f"- {p.nombre} | Ventas sin stock: {p.ventas_sin_stock}\n"

    enviar_mensaje(
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID,
        mensaje
    )
