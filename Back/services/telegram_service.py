# services/telegram_service.py
import asyncio
import aiohttp
import logging
import os
from sqlalchemy.orm import Session
from models.configuracion import Configuracion

logger = logging.getLogger(__name__)


class TelegramService:
    """Servicio mejorado para Telegram con soporte para múltiples números y variables de entorno"""
    
    def __init__(self):
        self.base_url = "https://api.telegram.org/bot"
    
    def _obtener_configuracion_env(self, clave: str, default: str = "") -> str:
        """Obtener configuración desde variables de entorno o desde la base de datos"""
        # Primero intentar desde variables de entorno
        env_value = os.getenv(clave)
        if env_value:
            return env_value
        
        # Si no existe en entorno, retornar default
        return default
    
    async def _enviar_mensaje_individual(self, token: str, chat_id: str, mensaje: str) -> bool:
        """Enviar mensaje a un número específico de Telegram"""
        try:
            url = f"{self.base_url}{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": mensaje,
                "parse_mode": "HTML"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"✅ Mensaje enviado a {chat_id}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Error enviando a {chat_id}: {response.status} - {error_text}")
                        return False
        except Exception as e:
            logger.error(f"❌ Excepción enviando a {chat_id}: {str(e)}")
            return False
    
    async def enviar_alertas(self, db: Session, mensaje: str) -> dict:
        """
        Enviar alertas a múltiples números de Telegram
        Retorna: {"exitos": [numeros], "fallos": [numeros]}
        """
        # Obtener configuración desde variables de entorno primero
        token = self._obtener_configuracion_env("TELEGRAM_BOT_TOKEN")
        numeros_alertas = self._obtener_configuracion_env("TELEGRAM_ALERTAS_NUMEROS")
        habilitado_env = self._obtener_configuracion_env("TELEGRAM_HABILITADO", "false")
        
        # Si no hay variables de entorno, usar la base de datos
        if not token:
            token = Configuracion.obtener_telegram_token(db)
        if not numeros_alertas:
            numeros_alertas = Configuracion.obtener_telegram_alertas(db)
        if habilitado_env == "false":
            # Verificar en la base de datos
            habilitado_db = db.query(Configuracion).filter(
                Configuracion.clave == "telegram_habilitado",
                Configuracion.valor == "true"
            ).first()
            if not habilitado_db:
                logger.info("📵 Telegram deshabilitado - no se envían alertas")
                return {"exitos": [], "fallos": [], "mensaje": "Telegram deshabilitado"}
        
        if not token:
            logger.error("❌ Token de Telegram no configurado")
            return {"exitos": [], "fallos": [], "mensaje": "Token no configurado"}
        
        if not numeros_alertas:
            logger.warning("⚠️ No hay números de alerta configurados")
            return {"exitos": [], "fallos": [], "mensaje": "No hay números configurados"}
        
        # Procesar números (separados por comas)
        numeros = [num.strip() for num in numeros_alertas.split(",") if num.strip()]
        
        if not numeros:
            logger.warning("⚠️ No se encontraron números válidos en la configuración")
            return {"exitos": [], "fallos": [], "mensaje": "No hay números válidos"}
        
        # Limitar a 2 números como solicitaste
        numeros = numeros[:2]
        
        # Enviar mensajes en paralelo
        tareas = []
        for numero in numeros:
            tarea = self._enviar_mensaje_individual(token, numero, mensaje)
            tareas.append((numero, tarea))
        
        # Esperar resultados
        resultados = await asyncio.gather(*[tarea for _, tarea in tareas], return_exceptions=True)
        
        # Procesar resultados
        exitos = []
        fallos = []
        
        for (numero, _), resultado in zip(tareas, resultados):
            if isinstance(resultado, Exception):
                fallos.append(numero)
                logger.error(f"❌ Error con {numero}: {str(resultado)}")
            elif resultado:
                exitos.append(numero)
            else:
                fallos.append(numero)
        
        logger.info(f"📊 Alertas enviadas: {len(exitos)} exitos, {len(fallos)} fallos")
        
        return {
            "exitos": exitos,
            "fallos": fallos,
            "total_enviados": len(exitos) + len(fallos)
        }
    
    async def enviar_backup(self, db: Session, mensaje: str) -> bool:
        """
        Enviar backup a un solo número de Telegram
        Retorna True/False indicando éxito
        """
        # Obtener configuración desde variables de entorno primero
        token = self._obtener_configuracion_env("TELEGRAM_BOT_TOKEN")
        numero_backup = self._obtener_configuracion_env("TELEGRAM_BACKUP_NUMERO")
        habilitado_env = self._obtener_configuracion_env("TELEGRAM_HABILITADO", "false")
        
        # Si no hay variables de entorno, usar la base de datos
        if not token:
            token = Configuracion.obtener_telegram_token(db)
        if not numero_backup:
            numero_backup = Configuracion.obtener_telegram_backup(db)
        if habilitado_env == "false":
            # Verificar en la base de datos
            habilitado_db = db.query(Configuracion).filter(
                Configuracion.clave == "telegram_habilitado",
                Configuracion.valor == "true"
            ).first()
            if not habilitado_db:
                logger.info("📵 Telegram deshabilitado - no se envía backup")
                return False
        
        if not token:
            logger.error("❌ Token de Telegram no configurado")
            return False
        
        if not numero_backup:
            logger.warning("⚠️ No hay número de backup configurado")
            return False
        
        # Enviar backup
        resultado = await self._enviar_mensaje_individual(token, numero_backup, mensaje)
        
        if resultado:
            logger.info(f"✅ Backup enviado a {numero_backup}")
        else:
            logger.error(f"❌ Error enviando backup a {numero_backup}")
        
        return resultado
    
    async def verificar_conexion(self, db: Session) -> dict:
        """
        Verificar la conexión con Telegram
        Retorna información sobre el estado del bot
        """
        # Obtener token desde variables de entorno o base de datos
        token = self._obtener_configuracion_env("TELEGRAM_BOT_TOKEN")
        if not token:
            token = Configuracion.obtener_telegram_token(db)
        
        if not token:
            return {"estado": "error", "mensaje": "Token no configurado"}
        
        try:
            url = f"{self.base_url}{token}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok"):
                            bot_info = data["result"]
                            return {
                                "estado": "conectado",
                                "bot_info": {
                                    "id": bot_info["id"],
                                    "username": bot_info["username"],
                                    "first_name": bot_info["first_name"]
                                }
                            }
                        else:
                            return {"estado": "error", "mensaje": "Token inválido"}
                    else:
                        return {"estado": "error", "mensaje": f"HTTP {response.status}"}
        except Exception as e:
            return {"estado": "error", "mensaje": str(e)}


# Instancia global del servicio
telegram_service = TelegramService()


# Funciones síncronas para compatibilidad con el código existente
def enviar_alertas_sync(db: Session, mensaje: str) -> dict:
    """Versión síncrona para enviar alertas"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(telegram_service.enviar_alertas(db, mensaje))


def enviar_backup_sync(db: Session, mensaje: str) -> bool:
    """Versión síncrona para enviar backup"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(telegram_service.enviar_backup(db, mensaje))


def verificar_conexion_sync(db: Session) -> dict:
    """Versión síncrona para verificar conexión"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(telegram_service.verificar_conexion(db))