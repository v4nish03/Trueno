from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from core.db_migrations import asegurar_columnas_catalogo
import os
from pathlib import Path

from routers import productos, ventas, alertas, reportes, devoluciones, movimientos, caja, sistema, configuracion
import models.caja  # noqa: F401 (Necesario para que SQLAlchemy registre las tablas)
import models.configuracion  # noqa: F401 (Necesario para que SQLAlchemy registre las tablas)

# Crear todas las tablas al iniciar
Base.metadata.create_all(bind=engine)
asegurar_columnas_catalogo(engine)

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

# ✅ Manejo global de errores inesperados persistente y proactivo
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    import traceback
    import asyncio
    import datetime
    from services.telegram_service import telegram_service
    
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    tb_str = traceback.format_exc()
    
    # Mensaje formateado para Telegram (HTML parse mode)
    error_msg = f"❌ <b>CRASH INTERNO TRUENO MOTORS</b> ❌\n\n"
    error_msg += f"<b>Fecha:</b> {fecha}\n"
    error_msg += f"<b>Ruta:</b> <code>{request.method} {request.url.path}</code>\n"
    error_msg += f"<b>Motivo:</b> {str(exc)}\n\n"
    error_msg += f"<b>Traza (resumen):</b>\n<pre>{tb_str[-1200:]}</pre>"
    
    # 1. Escribir en log local persistentemente
    try:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{fecha}] ERROR {request.method} {request.url.path}\n")
            f.write(tb_str)
            f.write("="*50 + "\n")
    except Exception:
        pass
        
    # 2. Notificar a Telegram (Asíncrono en background)
    try:
        asyncio.create_task(telegram_service.enviar_error_sistema(error_msg))
    except Exception:
        pass

    return JSONResponse(
        status_code=500,
        content={
            "error": "Fallo crítico en el servidor",
            "detalle": "Ocurrió un error no manejado. Se ha notificado al Telegram de los dueños y se guardó en el log de errores."
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
app.include_router(configuracion.router, prefix="/configuracion", tags=["Configuración"])


# ✅ Servir el Frontend Construido (Producción)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Front", "dist")
uploads_path = Path(__file__).resolve().parent / "uploads"
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Prefijos de API que NO deben ser interceptados por el catch-all de la SPA
API_PREFIXES = {
    "productos", "ventas", "devoluciones", "alertas",
    "reportes", "movimientos", "caja", "sistema",
    "configuracion", "health", "docs", "openapi.json", "redoc", "uploads"
}

if os.path.isdir(frontend_path):
    # Primero montar estáticos principales
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Catch-all para que Vue Router controle la navegación (Single Page Application)
    # Headers para que el navegador NUNCA cachee index.html
    # (los assets con hash en el nombre sí pueden cachearse — su nombre mismo cambia con cada build)
    _NO_CACHE = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_vue_spa(request: __import__('fastapi').Request, full_path: str):
        accept_header = request.headers.get("accept", "")
        index_html = os.path.join(frontend_path, "index.html")

        # Navegación directa del navegador → siempre index.html sin caché
        if "text/html" in accept_header:
            return FileResponse(index_html, headers=_NO_CACHE)

        # Archivos estáticos que existen (manifest.json, favicon, etc.)
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)

        # Fallback SPA: si el path no es un archivo estático conocido, devolver index.html
        # Esto cubre rutas de Vue Router como /pos, /ventas, /productos, etc.
        if full_path and not full_path.startswith(tuple(API_PREFIXES)):
            return FileResponse(index_html, headers=_NO_CACHE)

        return JSONResponse(status_code=404, content={"detail": "Not Found"})
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
