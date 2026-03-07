from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.configuracion import Configuracion
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ConfiguracionCreate(BaseModel):
    clave: str
    valor: Optional[str] = None
    descripcion: Optional[str] = None
    activo: bool = True


class ConfiguracionUpdate(BaseModel):
    valor: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None


@router.post("/")
def crear_configuracion(config: ConfiguracionCreate, db: Session = Depends(get_db)):
    """Crear una nueva configuración"""
    # Verificar si ya existe
    existente = db.query(Configuracion).filter(Configuracion.clave == config.clave).first()
    if existente:
        raise HTTPException(status_code=400, detail=f"La configuración '{config.clave}' ya existe")
    
    db_config = Configuracion(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.get("/")
def listar_configuraciones(db: Session = Depends(get_db)):
    """Listar todas las configuraciones"""
    return db.query(Configuracion).all()


@router.get("/{clave}")
def obtener_configuracion(clave: str, db: Session = Depends(get_db)):
    """Obtener una configuración por su clave"""
    config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    return config


@router.put("/{clave}")
def actualizar_configuracion(clave: str, config: ConfiguracionUpdate, db: Session = Depends(get_db)):
    """Actualizar una configuración"""
    db_config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    # Actualizar solo los campos proporcionados
    update_data = config.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_config, field, value)
    
    db.commit()
    db.refresh(db_config)
    return db_config


@router.delete("/{clave}")
def eliminar_configuracion(clave: str, db: Session = Depends(get_db)):
    """Eliminar una configuración"""
    config = db.query(Configuracion).filter(Configuracion.clave == clave).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    db.delete(config)
    db.commit()
    return {"message": f"Configuración '{clave}' eliminada correctamente"}


@router.post("/inicializar-telegram")
def inicializar_configuracion_telegram(db: Session = Depends(get_db)):
    """Inicializar las configuraciones básicas de Telegram"""
    configuraciones_basicas = [
        {
            "clave": "telegram_bot_token",
            "valor": "",
            "descripcion": "Token del bot de Telegram (obtener de @BotFather)",
            "activo": True
        },
        {
            "clave": "telegram_alertas_numeros",
            "valor": "",
            "descripcion": "Números de Telegram para alertas (separados por comas, ej: 123456789,987654321)",
            "activo": True
        },
        {
            "clave": "telegram_backup_numero",
            "valor": "",
            "descripcion": "Número de Telegram para backups (solo un número)",
            "activo": True
        },
        {
            "clave": "telegram_habilitado",
            "valor": "false",
            "descripcion": "Habilitar/deshabilitar envío de mensajes por Telegram",
            "activo": True
        }
    ]
    
    creados = []
    for config_data in configuraciones_basicas:
        existente = db.query(Configuracion).filter(Configuracion.clave == config_data["clave"]).first()
        if not existente:
            config = Configuracion(**config_data)
            db.add(config)
            creados.append(config_data["clave"])
    
    db.commit()
    
    return {
        "message": "Configuraciones de Telegram inicializadas",
        "creadas": creados,
        "instrucciones": {
            "telegram_bot_token": "Obtén un token hablando con @BotFather en Telegram",
            "telegram_alertas_numeros": "Agrega hasta 2 números de Telegram separados por comas",
            "telegram_backup_numero": "Agrega 1 número de Telegram para recibir backups",
            "telegram_habilitado": "Cambia a 'true' cuando todo esté configurado"
        }
    }
