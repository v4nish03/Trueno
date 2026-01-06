from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.producto import Producto
from models.venta import Venta, TipoVentaEnum, MetodoPagoEnum, EstadoVentaEnum
from models.venta_producto import VentaProducto
from models.movimiento import (
    MovimientoInventario,
    TipoMovimientoEnum,
    MotivoMovimientoEnum
)


def crear_venta(
    db: Session,
    items: list,
    metodo_pago: MetodoPagoEnum
):
    """
    productos = [
        {
            "producto_id": int,
            "cantidad": int,
            "precio_unitario": float
        }
    ]
    """

    try:
        total = 0
        venta_sin_stock = False

        # 1️⃣ Crear venta temporal
        venta = Venta(
            total=0,
            tipo=TipoVentaEnum.normal,
            metodo_pago=metodo_pago,
            estado=EstadoVentaEnum.completa
        )
        db.add(venta)
        db.flush()  # obtenemos venta.id

        # 2️⃣ Procesar productos
        for item in items:
            producto = db.query(Producto).filter(
                Producto.id == item["producto_id"]
            ).first()

            if not producto:
                raise Exception("Producto no encontrado")

            cantidad = item["cantidad"]
            precio = item["precio_unitario"]

            # 3️⃣ Registrar producto en la venta
            vp = VentaProducto(
                venta_id=venta.id,
                producto_id=producto.id,
                cantidad=cantidad,
                precio_unitario=precio
            )
            db.add(vp)

            # 4️⃣ Movimiento de inventario
            movimiento = MovimientoInventario(
                producto_id=producto.id,
                tipo=TipoMovimientoEnum.salida,
                motivo=MotivoMovimientoEnum.venta,
                cantidad=cantidad,
                referencia_id=venta.id
            )
            db.add(movimiento)

            # 5️⃣ Stock o venta sin stock
            if producto.stock >= cantidad:
                producto.stock -= cantidad
            else:
                venta_sin_stock = True
                producto.ventas_sin_stock += 1

            total += cantidad * precio

        # 6️⃣ Finalizar venta
        venta.total = total
        if venta_sin_stock:
            venta.tipo = TipoVentaEnum.sin_stock

        db.commit()
        return venta

    except SQLAlchemyError as e:
        db.rollback()
        raise e

# services/venta_service.py

def crear_venta_abierta(db: Session):
    """Crea una venta vacía en estado 'abierta'"""
    venta = Venta(estado=EstadoVentaEnum.abierta)
    db.add(venta)
    db.commit()
    return venta

def agregar_producto_a_venta(
    db: Session,
    venta_id: int,
    producto_id: int,
    cantidad: int,
    precio_unitario: float
):
    """Agrega productos a una venta abierta"""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    
    if venta.estado != EstadoVentaEnum.abierta:
        raise Exception("Solo se pueden agregar productos a ventas abiertas")
    
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    
    # Registrar en venta_productos
    vp = VentaProducto(
        venta_id=venta.id,
        producto_id=producto.id,
        cantidad=cantidad,
        precio_unitario=precio_unitario
    )
    db.add(vp)
    
    # Generar movimiento pero NO descontar stock todavía
    # (solo se descuenta al cerrar)
    
    db.commit()
    return vp

def cerrar_venta(
    db: Session,
    venta_id: int,
    metodo_pago: MetodoPagoEnum
):
    """Cierra la venta, calcula total, descuenta stock"""
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    
    if venta.estado != EstadoVentaEnum.abierta:
        raise Exception("La venta ya está cerrada")
    
    productos_venta = db.query(VentaProducto).filter(
        VentaProducto.venta_id == venta_id
    ).all()
    
    total = 0
    venta_sin_stock = False
    
    for vp in productos_venta:
        producto = db.query(Producto).filter(Producto.id == vp.producto_id).first()
        
        # Descontar stock
        if producto.stock >= vp.cantidad:
            producto.stock -= vp.cantidad
        else:
            venta_sin_stock = True
            producto.ventas_sin_stock += 1
        
        # Movimiento de inventario
        movimiento = MovimientoInventario(
            producto_id=producto.id,
            tipo=TipoMovimientoEnum.salida,
            motivo=MotivoMovimientoEnum.venta,
            cantidad=vp.cantidad,
            referencia_id=venta.id
        )
        db.add(movimiento)
        
        total += vp.cantidad * vp.precio_unitario
    
    # Actualizar venta
    venta.total = total
    venta.metodo_pago = metodo_pago
    venta.tipo = TipoVentaEnum.sin_stock if venta_sin_stock else TipoVentaEnum.normal
    venta.estado = EstadoVentaEnum.completa
    
    db.commit()
    
    # Enviar alertas si hay ventas sin stock
    if venta_sin_stock:
        from services.alertas_service import enviar_alertas
        enviar_alertas(db)
    
    return venta