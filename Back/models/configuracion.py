from sqlalchemy import Column, Integer, String, Boolean, Text
from database import Base


class Configuracion(Base):
    __tablename__ = "configuracion"
    
    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String(100), unique=True, nullable=False, index=True)
    valor = Column(Text, nullable=True)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, default=True)
    
    # Configuraciones específicas para Telegram
    @classmethod
    def obtener_telegram_alertas(cls, db):
        """Obtener números de Telegram para alertas (separados por comas)"""
        config = db.query(cls).filter(
            cls.clave == "telegram_alertas_numeros",
            cls.activo.is_(True)
        ).first()
        return config.valor if config else ""
    
    @classmethod
    def obtener_telegram_backup(cls, db):
        """Obtener número de Telegram para backups"""
        config = db.query(cls).filter(
            cls.clave == "telegram_backup_numero", 
            cls.activo.is_(True)
        ).first()
        return config.valor if config else ""
    
    @classmethod
    def obtener_telegram_token(cls, db):
        """Obtener token del bot de Telegram"""
        config = db.query(cls).filter(
            cls.clave == "telegram_bot_token",
            cls.activo.is_(True)
        ).first()
        return config.valor if config else ""
