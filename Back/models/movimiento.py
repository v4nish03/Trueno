# models/movimiento.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from core.database import Base
import enum

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

    id = Column(Integer, primary_key=True, index=True)

    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    tipo = Column(Enum(TipoMovimientoEnum), nullable=False)
    motivo = Column(Enum(MotivoMovimientoEnum), nullable=False)

    cantidad = Column(Integer, nullable=False)

    referencia_id = Column(Integer, nullable=True)
    # Ej: id de venta, id de devolución (a futuro)

    fecha = Column(DateTime(timezone=True), server_default=func.now())
