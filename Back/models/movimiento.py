from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class TipoMovimientoEnum(enum.Enum):
    ingreso = "ingreso"
    salida = "salida"
    ajuste = "ajuste"


class MotivoMovimientoEnum(enum.Enum):
    compra = "compra"
    venta = "venta"
    devolucion = "devolucion"
    stock_inicial = "stock_inicial"
    correccion = "correccion"


class MovimientoInventario(Base):
    __tablename__ = "movimientos_inventario"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_movimiento_cantidad_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)

    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)
    producto = relationship("Producto", back_populates="movimientos")

    tipo = Column(Enum(TipoMovimientoEnum), nullable=False)
    motivo = Column(Enum(MotivoMovimientoEnum), nullable=False)

    cantidad = Column(Integer, nullable=False)

    referencia_id = Column(Integer, nullable=True)

    fecha = Column(DateTime(timezone=True), server_default=func.now())
