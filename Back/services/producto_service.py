from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.producto import Producto, UbicacionProducto
from services.inventario_service import ingreso_stock, ajuste_stock
from models.movimiento import MotivoMovimientoEnum
from typing import Optional


def crear_producto(
    db: Session,
    *,
    codigo: str,
    nombre: str,
    precio1: float,
    precio2: float | None = None,
    precio3: float | None = None,
    precio4: float | None = None,
    stock_inicial: int = 0,
    stock_minimo: int = 5,
    ubicacion: str = "tienda",
    descripcion: str | None = None
):
    # Validar que el código no exista
    existe = db.query(Producto).filter(Producto.codigo == codigo).first()
    if existe:
        raise Exception(f"Ya existe un producto con el código '{codigo}'")

    if ubicacion not in {"tienda", "bodega"}:
        raise Exception("Ubicación inválida. Usa 'tienda' o 'bodega'")

    ubicacion_enum = UbicacionProducto.TIENDA if ubicacion == "tienda" else UbicacionProducto.BODEGA

    producto = Producto(
        codigo=codigo,
        nombre=nombre,
        descripcion=descripcion,
        precio1=precio1,
        precio2=precio2,
        precio3=precio3,
        precio4=precio4,
        stock=0,  # SIEMPRE empieza en 0
        stock_minimo=stock_minimo,
        ubicacion=ubicacion_enum,
        activo=True
    )

    db.add(producto)
    db.flush()  # para obtener producto.id antes del commit

    if stock_inicial > 0:
        ingreso_stock(
            db,
            producto=producto,
            cantidad=stock_inicial,
            motivo=MotivoMovimientoEnum.stock_inicial
        )

    db.commit()
    db.refresh(producto)
    return producto


def listar_productos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    buscar: Optional[str] = None,
    solo_activos: bool = True
):
    query = db.query(Producto)

    if solo_activos:
        query = query.filter(Producto.activo == True)

    if buscar:
        query = query.filter(
            or_(
                Producto.nombre.ilike(f"%{buscar}%"),
                Producto.codigo.ilike(f"%{buscar}%")
            )
        )

    return query.order_by(Producto.nombre).offset(skip).limit(limit).all()


def obtener_producto(db: Session, producto_id: int):
    return db.query(Producto).filter(Producto.id == producto_id).first()


def obtener_producto_por_codigo(db: Session, codigo: str):
    return db.query(Producto).filter(Producto.codigo == codigo).first()


def actualizar_producto(
    db: Session,
    producto_id: int,
    producto_data: dict
):
    producto = obtener_producto(db, producto_id)
    if not producto:
        raise Exception("Producto no encontrado")

    # Convertir ubicacion string a enum si viene en los datos
    if "ubicacion" in producto_data and producto_data["ubicacion"]:
        ubicacion_str = producto_data["ubicacion"]
        if ubicacion_str not in {"tienda", "bodega"}:
            raise Exception("Ubicación inválida. Usa 'tienda' o 'bodega'")
        producto_data["ubicacion"] = (
            UbicacionProducto.TIENDA if ubicacion_str == "tienda"
            else UbicacionProducto.BODEGA
        )

    for key, value in producto_data.items():
        if value is not None and hasattr(producto, key):
            setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto


def descontinuar_producto(db: Session, producto_id: int):
    producto = obtener_producto(db, producto_id)
    if not producto:
        raise Exception("Producto no encontrado")

    producto.activo = False
    db.commit()
    return {
        "mensaje": f"Producto '{producto.nombre}' descontinuado",
        "producto_id": producto_id
    }


def reactivar_producto(db: Session, producto_id: int):
    producto = obtener_producto(db, producto_id)
    if not producto:
        raise Exception("Producto no encontrado")

    producto.activo = True
    db.commit()
    return {
        "mensaje": f"Producto '{producto.nombre}' reactivado",
        "producto_id": producto_id
    }


def obtener_historial(db: Session, producto_id: int):
    from models.movimiento import MovimientoInventario

    producto = obtener_producto(db, producto_id)
    if not producto:
        raise Exception("Producto no encontrado")

    movimientos = db.query(MovimientoInventario).filter(
        MovimientoInventario.producto_id == producto_id
    ).order_by(MovimientoInventario.fecha.desc()).all()

    return {
        "producto": {
            "id": producto.id,
            "codigo": producto.codigo,
            "nombre": producto.nombre,
            "stock_actual": producto.stock
        },
        "total_movimientos": len(movimientos),
        "movimientos": [
            {
                "id": m.id,
                "tipo": m.tipo.value,
                "motivo": m.motivo.value,
                "cantidad": m.cantidad,
                "fecha": m.fecha,
                "referencia_id": m.referencia_id
            }
            for m in movimientos
        ]
    }


def ingresar_stock_producto(
    db: Session,
    producto_id: int,
    cantidad: int,
    motivo: str = "compra"
):
    """
    Registra el ingreso de mercadería a un producto existente.
    Motivos válidos: 'compra', 'devolucion', 'correccion'
    """
    producto = obtener_producto(db, producto_id)
    if not producto:
        raise Exception("Producto no encontrado")

    if not producto.activo:
        raise Exception("No se puede ingresar stock a un producto descontinuado")

    if cantidad <= 0:
        raise Exception("La cantidad debe ser mayor a 0")

    # Mapear string a enum
    motivos_validos = {
        "compra": MotivoMovimientoEnum.compra,
        "devolucion": MotivoMovimientoEnum.devolucion,
        "correccion": MotivoMovimientoEnum.correccion,
    }

    if motivo not in motivos_validos:
        raise Exception(f"Motivo inválido. Usa: {list(motivos_validos.keys())}")

    motivo_enum = motivos_validos[motivo]

    stock_antes = producto.stock

    ingreso_stock(
        db,
        producto=producto,
        cantidad=cantidad,
        motivo=motivo_enum
    )

    db.commit()
    db.refresh(producto)

    return {
        "mensaje": "Ingreso de stock registrado correctamente",
        "producto_id": producto.id,
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "motivo": motivo,
        "cantidad_ingresada": cantidad,
        "stock_anterior": stock_antes,
        "stock_nuevo": producto.stock
    }


def ajustar_stock_manual(
    db: Session,
    producto_id: int,
    nuevo_stock: int
):
    """
    Ajuste manual de stock para correcciones de inventario físico.
    Registra el movimiento con motivo 'correccion'.
    """
    producto = obtener_producto(db, producto_id)
    if not producto:
        raise Exception("Producto no encontrado")

    if nuevo_stock < 0:
        raise Exception("El stock no puede ser negativo")

    # ✅ CORREGIDO: guardar stock anterior ANTES de modificar
    stock_anterior = producto.stock

    ajuste_stock(
        db,
        producto=producto,
        cantidad=nuevo_stock,
        motivo=MotivoMovimientoEnum.correccion
    )

    db.commit()
    db.refresh(producto)

    return {
        "mensaje": "Stock ajustado correctamente",
        "producto_id": producto.id,
        "codigo": producto.codigo,
        "nombre": producto.nombre,
        "stock_anterior": stock_anterior,
        "stock_nuevo": producto.stock
    }