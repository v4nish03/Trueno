from sqlalchemy import Column, Integer, Float, Enum, DateTime
from sqlalchemy.sql import func
from database import Base
import enum
from sqlalchemy.orm import relationship


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

    id = Column(Integer, primary_key=True, index=True)

    # relaciones
    productos = relationship("VentaProducto", backref="venta")

    # datos principales
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    total = Column(Float, nullable=True)  # 🔥 se calcula al cerrar

    tipo = Column(
        Enum(TipoVentaEnum),
        nullable=True  # 🔥 se define al cerrar
    )

    metodo_pago = Column(
        Enum(MetodoPagoEnum),
        nullable=True  # 🔥 se define al cerrar
    )

    estado = Column(
        Enum(EstadoVentaEnum),
        default=EstadoVentaEnum.abierta
    )
