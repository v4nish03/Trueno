from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Enum,
    Text
)
from sqlalchemy.sql import func
import enum
from sqlalchemy.orm import relationship
from database import Base


# Enum para ubicación
class UbicacionProducto(enum.Enum):
    TIENDA = "tienda"
    BODEGA = "bodega"


class Producto(Base):
    __tablename__ = "productos"

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
        default=UbicacionProducto.TIENDA
    )

    activo = Column(Boolean, nullable=False, default=True)

    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_edicion = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )