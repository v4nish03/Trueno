from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from services import producto_service
from typing import List, Optional

router = APIRouter()


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
    db: Session = Depends(get_db)
):
    """Listar todos los productos. Soporta búsqueda por nombre o código."""
    productos = producto_service.listar_productos(db, skip, limit, buscar, solo_activos)
    # ✅ Convertir lista de objetos ORM a lista de schemas
    return [ProductoResponse.from_orm(p) for p in productos]


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