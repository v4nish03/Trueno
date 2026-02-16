# models/venta_producto.py
from sqlalchemy import Column, Integer, Float, ForeignKey
from database import Base

class VentaProducto(Base):
    __tablename__ = "venta_productos"

    id = Column(Integer, primary_key=True, index=True)

    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    cantidad = Column(Integer, nullable=False)

    precio_unitario = Column(Float, nullable=False)
