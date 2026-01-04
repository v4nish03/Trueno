# services/recibo_service.py
from sqlalchemy.orm import Session
from models.recibo import Recibo
import uuid


def generar_recibo(db: Session, *, venta_id: int):
    recibo = Recibo(
        venta_id=venta_id,
        codigo_qr=str(uuid.uuid4())
    )
    db.add(recibo)
    return recibo
