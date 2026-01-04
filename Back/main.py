from fastapi import FastAPI
from database import Base, engine

from routers import productos, ventas, alertas, reportes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Inventario y Ventas")

app.include_router(productos.router, prefix="/productos", tags=["Productos"])
app.include_router(ventas.router, prefix="/ventas", tags=["Ventas"])
app.include_router(alertas.router, prefix="/alertas", tags=["Alertas"])
app.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
