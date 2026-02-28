from sqlalchemy import CheckConstraint, Column, DateTime, Enum, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class TipoVentaEnum(enum.Enum):
    normal = "normal"
    sin_stock = "sin_stock"


class MetodoPagoEnum(enum.Enum):
    efectivo = "efectivo"
    qr = "qr"


class EstadoVentaEnum(enum.Enum):
    abierta = "abierta"
    completa = "completa"
    anulada = "anulada"


class Venta(Base):
    __tablename__ = "ventas"
    __table_args__ = (
        CheckConstraint("total IS NULL OR total >= 0", name="ck_venta_total_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True)

    turno_id = Column(Integer, ForeignKey("turnos_caja.id"), nullable=True)

    productos = relationship("VentaProducto", backref="venta", cascade="all, delete-orphan")

    fecha = Column(DateTime(timezone=True), server_default=func.now())

    total = Column(Float, nullable=True)

    tipo = Column(Enum(TipoVentaEnum), nullable=True)

    metodo_pago = Column(Enum(MetodoPagoEnum), nullable=True)

    estado = Column(Enum(EstadoVentaEnum), default=EstadoVentaEnum.abierta)
