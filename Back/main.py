from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
import os

from routers import productos, ventas, alertas, reportes, devoluciones, movimientos, caja, sistema
import models.caja

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
app.include_router(movimientos.router,  prefix="/movimientos",  tags=["Movimientos"])
app.include_router(caja.router,         prefix="/caja",         tags=["Caja"])
app.include_router(sistema.router,      prefix="/sistema",      tags=["Sistema"])


# ✅ Servir el Frontend Construido (Producción)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Front", "dist")

if os.path.isdir(frontend_path):
    # Primero montar estáticos principales
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Catch-all para que Vue Router controle la navegación (Single Page Application)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_vue_spa(full_path: str):
        # Ignorar peticiones a las rutas exclusivas de API o docs si no emparejaron
        if full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return {"detail": "Not Found"}
            
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Cualquier otra ruta devuelve el index.html
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    @app.get("/", tags=["Sistema"])
    def raiz():
        return {
            "sistema": "Trueno Motors - Desarrollo",
            "estado": "Frontend no compilado. Usa 'npm run build' en la carpeta Front."
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