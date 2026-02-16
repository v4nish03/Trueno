from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import os

from routers import productos, ventas, alertas, reportes, devoluciones

# Crear todas las tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Inventario y Ventas - Trueno Motors",
    description="API para gestión de inventario, ventas y reportes de Trueno Motors Uyuni",
    version="1.0.0"
)

# ✅ CORS — permite que el frontend (Vue, Flutter, etc.) se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambia esto por la URL real del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Manejo global de errores inesperados
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detalle": str(exc)
        }
    )

# ✅ Routers
app.include_router(productos.router,    prefix="/productos",    tags=["Productos"])
app.include_router(ventas.router,       prefix="/ventas",       tags=["Ventas"])
app.include_router(devoluciones.router, prefix="/devoluciones", tags=["Devoluciones"])
app.include_router(alertas.router,      prefix="/alertas",      tags=["Alertas"])
app.include_router(reportes.router,     prefix="/reportes",     tags=["Reportes"])


# ✅ Endpoint raíz — sirve para verificar que el servidor está corriendo
@app.get("/", tags=["Sistema"])
def raiz():
    return {
        "sistema": "Trueno Motors - Sistema de Inventario y Ventas",
        "version": "1.0.0",
        "estado": "activo",
        "docs": "/docs"
    }


@app.get("/health", tags=["Sistema"])
def health_check():
    """Verificar que la API y la base de datos están funcionando"""
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        return {"estado": "ok", "base_de_datos": "conectada"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"estado": "error", "detalle": str(e)}
        )