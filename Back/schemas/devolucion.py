from pydantic import BaseModel, Field


class DevolucionRequest(BaseModel):
    producto_id: int = Field(..., description="ID del producto a devolver")
    cantidad: int = Field(..., gt=0, description="Cantidad a devolver (debe ser mayor a 0)")


class DevolucionResponse(BaseModel):
    mensaje: str
    venta_id: int
    producto_id: int
    cantidad_devuelta: int
    monto_devuelto: float
    nuevo_total_venta: float
    stock_actual_producto: int