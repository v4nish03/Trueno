from sqlalchemy import CheckConstraint, Column, Float, ForeignKey, Integer

from database import Base


class VentaProducto(Base):
    __tablename__ = "venta_productos"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_venta_producto_cantidad_positive"),
        CheckConstraint("precio_unitario > 0", name="ck_venta_producto_precio_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)

    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False)

    cantidad = Column(Integer, nullable=False)

    precio_unitario = Column(Float, nullable=False)
