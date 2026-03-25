from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from services import producto_service
from typing import List, Optional
from pathlib import Path
from uuid import uuid4
from fastapi.responses import Response
from services.catalogo_pdf_service import generar_catalogo_pdf

router = APIRouter()
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads" / "productos"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=ProductoResponse)
def crear(producto: ProductoCreate, db: Session = Depends(get_db)):
    """Crear un nuevo producto con stock inicial opcional"""
    try:
        producto_creado = producto_service.crear_producto(db, **producto.model_dump())
        # ✅ Ahora simplemente devuelve el objeto, Pydantic lo convierte
        return ProductoResponse.from_orm(producto_creado)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ProductoResponse])
def listar(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    buscar: Optional[str] = None,
    solo_activos: bool = True,
    categoria: Optional[str] = Query(None, description="Filtrar por categoría exacta"),
    solo_con_imagen: bool = Query(False, description="Solo productos con imagen"),
    db: Session = Depends(get_db)
):
    """Listar todos los productos. Soporta búsqueda por nombre o código."""
    productos = producto_service.listar_productos(
        db,
        skip,
        limit,
        buscar,
        solo_activos,
        categoria,
        solo_con_imagen,
    )
    # ✅ Convertir lista de objetos ORM a lista de schemas
    return [ProductoResponse.from_orm(p) for p in productos]


@router.get("/categorias", response_model=List[str])
def categorias(
    solo_activos: bool = True,
    db: Session = Depends(get_db)
):
    """Lista de categorías disponibles para filtros o catálogos."""
    return producto_service.listar_categorias(db, solo_activos)


@router.post("/upload-imagen", response_model=dict)
async def upload_imagen_producto(
    archivo: UploadFile = File(...),
):
    """Sube imagen local y devuelve URL pública para asociar al producto."""
    tipos_permitidos = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    ext = tipos_permitidos.get(archivo.content_type)
    if not ext:
        raise HTTPException(status_code=400, detail="Formato no permitido. Usa JPG, PNG o WEBP")

    nombre_archivo = f"{uuid4().hex}{ext}"
    destino = UPLOADS_DIR / nombre_archivo

    contenido = await archivo.read()
    if len(contenido) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="La imagen excede 5MB")

    with open(destino, "wb") as f:
        f.write(contenido)

    return {
        "mensaje": "Imagen subida correctamente",
        "url": f"/uploads/productos/{nombre_archivo}"
    }


@router.get("/catalogo-pdf")
def descargar_catalogo_pdf(
    request: Request,
    categorias: Optional[List[str]] = Query(None, description="Categorías a incluir. Repetir parámetro para múltiples."),
    solo_activos: bool = True,
    solo_con_imagen: bool = False,
    db: Session = Depends(get_db),
):
    """
    Genera un PDF real del catálogo (no captura de pantalla):
    portada + productos segmentados por categoría.
    """
    categorias_query = (categorias or []) + request.query_params.getlist("categorias[]")
    categorias_limpias = [c.strip() for c in categorias_query if c and c.strip()]

    productos_por_categoria = {}

    if not categorias_limpias:
        productos = producto_service.listar_productos(
            db,
            skip=0,
            limit=2000,
            buscar=None,
            solo_activos=solo_activos,
            categoria=None,
            solo_con_imagen=solo_con_imagen,
        )
        for p in productos:
            categoria = p.categoria or "General"
            productos_por_categoria.setdefault(categoria, []).append(p)
    else:
        for categoria in categorias_limpias:
            productos = producto_service.listar_productos(
                db,
                skip=0,
                limit=2000,
                buscar=None,
                solo_activos=solo_activos,
                categoria=categoria,
                solo_con_imagen=solo_con_imagen,
            )
            productos_por_categoria[categoria] = productos

    if not productos_por_categoria:
        raise HTTPException(status_code=404, detail="No hay productos para generar el catálogo")

    pdf_bytes = generar_catalogo_pdf(productos_por_categoria, categorias_limpias)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="catalogo_productos.pdf"'},
    )


@router.get("/codigo/{codigo}", response_model=ProductoResponse)
def obtener_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """Buscar producto por código (útil para lectores de código de barras)"""
    producto = producto_service.obtener_producto_por_codigo(db, codigo)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoResponse.from_orm(producto)


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener(producto_id: int, db: Session = Depends(get_db)):
    """Obtener un producto por ID con todos sus datos"""
    producto = producto_service.obtener_producto(db, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoResponse.from_orm(producto)


@router.put("/{producto_id}", response_model=dict)
def actualizar(
    producto_id: int,
    producto_data: ProductoUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar datos de un producto (no afecta el stock)"""
    try:
        producto = producto_service.actualizar_producto(
            db,
            producto_id,
            producto_data.model_dump(exclude_unset=True)
        )
        return {
            "mensaje": "Producto actualizado correctamente",
            "producto": ProductoResponse.from_orm(producto).model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{producto_id}")
def descontinuar(producto_id: int, db: Session = Depends(get_db)):
    """Marcar producto como descontinuado (no se elimina, queda en historial)"""
    try:
        return producto_service.descontinuar_producto(db, producto_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{producto_id}/reactivar")
def reactivar(producto_id: int, db: Session = Depends(get_db)):
    """Reactivar un producto descontinuado"""
    try:
        return producto_service.reactivar_producto(db, producto_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{producto_id}/ingresar-stock")
def ingresar_stock(
    producto_id: int,
    cantidad: int = Query(..., gt=0, description="Cantidad a ingresar"),
    motivo: str = Query("compra", description="Motivo: compra, devolucion, correccion"),
    db: Session = Depends(get_db)
):
    """
    Registra el ingreso de mercadería a un producto.
    Úsalo cuando llegue nueva mercadería a la tienda.
    """
    try:
        return producto_service.ingresar_stock_producto(db, producto_id, cantidad, motivo)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{producto_id}/ajustar-stock")
def ajustar_stock(
    producto_id: int,
    nuevo_stock: int = Query(..., ge=0, description="Nuevo valor de stock"),
    db: Session = Depends(get_db)
):
    """
    Ajuste manual de stock (para cuando el inventario físico no coincide).
    Registra el cambio como movimiento de corrección.
    """
    try:
        return producto_service.ajustar_stock_manual(db, producto_id, nuevo_stock)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{producto_id}/historial")
def historial_movimientos(producto_id: int, db: Session = Depends(get_db)):
    """Ver historial completo de movimientos de inventario de un producto"""
    try:
        return producto_service.obtener_historial(db, producto_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
