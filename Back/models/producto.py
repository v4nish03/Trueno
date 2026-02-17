from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class UbicacionProducto(enum.Enum):
    TIENDA = "tienda"
    BODEGA = "bodega"


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        CheckConstraint("stock >= 0", name="ck_producto_stock_non_negative"),
        CheckConstraint("stock_minimo >= 0", name="ck_producto_stock_minimo_non_negative"),
        CheckConstraint("ventas_sin_stock >= 0", name="ck_producto_ventas_sin_stock_non_negative"),
        CheckConstraint("precio1 > 0", name="ck_producto_precio1_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)

    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)

    precio1 = Column(Float, nullable=False)
    precio2 = Column(Float, nullable=True)
    precio3 = Column(Float, nullable=True)
    precio4 = Column(Float, nullable=True)

    stock = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=5)
    ventas_sin_stock = Column(Integer, nullable=False, default=0)

    movimientos = relationship("MovimientoInventario", back_populates="producto")

    ubicacion = Column(
        Enum(UbicacionProducto),
        nullable=False,
        default=UbicacionProducto.TIENDA,
    )

    activo = Column(Boolean, nullable=False, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_edicion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
