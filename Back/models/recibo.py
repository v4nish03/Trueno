# models/recibo.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class Recibo(Base):
    __tablename__ = "recibos"

    id = Column(Integer, primary_key=True, index=True)

    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)

    codigo_qr = Column(String, unique=True, nullable=False)

    fecha_impresion = Column(DateTime(timezone=True), server_default=func.now())
