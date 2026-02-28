from sqlalchemy import Column, DateTime, Enum, Float, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base

class EstadoTurnoEnum(enum.Enum):
    abierto = "abierto"
    cerrado = "cerrado"

class TurnoCaja(Base):
    __tablename__ = "turnos_caja"

    id = Column(Integer, primary_key=True, index=True)
    
    fecha_apertura = Column(DateTime(timezone=True), server_default=func.now())
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    
    monto_inicial = Column(Float, default=0.0)
    estado = Column(Enum(EstadoTurnoEnum), default=EstadoTurnoEnum.abierto)

    # Relación bidireccional se definirá en el backref de Venta.
