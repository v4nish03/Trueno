# models/venta.py
from sqlalchemy import Column, Integer, Float, Enum, DateTime
from sqlalchemy.sql import func
from core.database import Base
import enum

class TipoVentaEnum(enum.Enum):
    normal = "normal"
    sin_stock = "sin_stock"

class MetodoPagoEnum(enum.Enum):
    efectivo = "efectivo"
    qr = "qr"

class EstadoVentaEnum(enum.Enum):
    completa = "completa"
    parcial = "parcial"
    anulada = "anulada"

class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)

    fecha = Column(DateTime(timezone=True), server_default=func.now())

    total = Column(Float, nullable=False)

    tipo = Column(Enum(TipoVentaEnum), nullable=False)
    metodo_pago = Column(Enum(MetodoPagoEnum), nullable=False)
    estado = Column(Enum(EstadoVentaEnum), default=EstadoVentaEnum.completa)
