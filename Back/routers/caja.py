from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_db
from models.caja import TurnoCaja, EstadoTurnoEnum
from models.venta import Venta, EstadoVentaEnum, MetodoPagoEnum

router = APIRouter()

class AbrirCajaRequest(BaseModel):
    monto_inicial: float

@router.get("/estado")
def estado_caja(db: Session = Depends(get_db)):
    turno = db.query(TurnoCaja).filter(TurnoCaja.estado == EstadoTurnoEnum.abierto).first()
    if not turno:
        return {"abierta": False, "turno": None}
    
    # Calcular ingresos
    efectivo = db.query(func.sum(Venta.total)).filter(
        Venta.turno_id == turno.id, 
        Venta.metodo_pago == MetodoPagoEnum.efectivo,
        Venta.estado == EstadoVentaEnum.completa
    ).scalar() or 0.0
    
    qr = db.query(func.sum(Venta.total)).filter(
        Venta.turno_id == turno.id, 
        Venta.metodo_pago == MetodoPagoEnum.qr,
        Venta.estado == EstadoVentaEnum.completa
    ).scalar() or 0.0

    total_esperado_caja = turno.monto_inicial + efectivo

    return {
        "abierta": True,
        "turno": {
            "id": turno.id,
            "fecha_apertura": turno.fecha_apertura,
            "monto_inicial": turno.monto_inicial,
            "ingresos_efectivo": efectivo,
            "ingresos_qr": qr,
            "total_esperado_caja": total_esperado_caja
        }
    }

@router.post("/abrir")
def abrir_caja(req: AbrirCajaRequest, db: Session = Depends(get_db)):
    if req.monto_inicial < 0:
        raise HTTPException(status_code=400, detail="El monto inicial no puede ser negativo.")

    abierto = db.query(TurnoCaja).filter(TurnoCaja.estado == EstadoTurnoEnum.abierto).first()
    if abierto:
        raise HTTPException(status_code=400, detail="Ya hay un turno de caja abierto.")
    
    nuevo_turno = TurnoCaja(monto_inicial=req.monto_inicial)
    db.add(nuevo_turno)
    db.commit()
    db.refresh(nuevo_turno)
    return nuevo_turno

@router.post("/cerrar")
def cerrar_caja(db: Session = Depends(get_db)):
    turno = db.query(TurnoCaja).filter(TurnoCaja.estado == EstadoTurnoEnum.abierto).first()
    if not turno:
        raise HTTPException(status_code=400, detail="No hay ningun turno abierto.")
    
    turno.estado = EstadoTurnoEnum.cerrado
    turno.fecha_cierre = func.now()
    db.commit()
    return {"mensaje": "Caja cerrada correctamente", "turno_id": turno.id}
