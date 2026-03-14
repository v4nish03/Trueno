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
        Enviar alertas a múltiples números de Telegram.
        Lee TELEGRAM_TOKEN y TELEGRAM_CHAT_ID (separados por coma) del .env.
        """
        # --- Leer variables del .env (nombres reales del proyecto) ---
        token = self._obtener_configuracion_env("TELEGRAM_TOKEN")
        numeros_alertas = self._obtener_configuracion_env("TELEGRAM_CHAT_ID")
        habilitado_env = self._obtener_configuracion_env("TELEGRAM_HABILITADO", "false")

        # Si no hay variables de entorno, caer a base de datos
        if not token:
            token = Configuracion.obtener_telegram_token(db)
        if not numeros_alertas:
            numeros_alertas = Configuracion.obtener_telegram_alertas(db)

        # Si hay token y números en el .env, consideramos Telegram habilitado
        # aunque TELEGRAM_HABILITADO no esté seteado explícitamente
        if habilitado_env.lower() not in ("true", "1", "si", "yes"):
            if token and numeros_alertas:
                # Hay configuración completa en .env → habilitado automáticamente
                habilitado_env = "true"
            else:
                # Sin config en .env, verificar BD
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

        # Procesar números (separados por comas, máximo 2)
        numeros = [num.strip() for num in numeros_alertas.split(",") if num.strip()][:2]

        if not numeros:
            return {"exitos": [], "fallos": [], "mensaje": "No hay números válidos"}

        # Enviar mensajes en paralelo
        tareas = [(num, self._enviar_mensaje_individual(token, num, mensaje)) for num in numeros]
        resultados = await asyncio.gather(*[t for _, t in tareas], return_exceptions=True)

        exitos, fallos = [], []
        for (numero, _), resultado in zip(tareas, resultados):
            if isinstance(resultado, Exception) or not resultado:
                fallos.append(numero)
                logger.error(f"❌ Error con {numero}: {resultado}")
            else:
                exitos.append(numero)

        logger.info(f"📊 Alertas enviadas: {len(exitos)} éxitos, {len(fallos)} fallos")
        return {"exitos": exitos, "fallos": fallos, "total_enviados": len(exitos) + len(fallos)}
    
    async def enviar_error_sistema(self, mensaje: str) -> bool:
        """Enviar un registro de caída o error crítico por Telegram al dueño (Chat ID Backup)"""
        token = self._obtener_configuracion_env("TELEGRAM_TOKEN")
        chat_id_backup = self._obtener_configuracion_env("TELEGRAM_CHAT_ID_BACKUP")
        habilitado_env = self._obtener_configuracion_env("TELEGRAM_HABILITADO", "false")
        
        if habilitado_env.lower() != "true" or not token or not chat_id_backup:
            return False
            
        # Utilizamos el chat ID de backup pues suele ser el del Administrador/Dueño de la red de Trueno Motors
        return await self._enviar_mensaje_individual(token, chat_id_backup, mensaje)

    async def enviar_backup(self, db: Session, mensaje: str) -> bool:
        """
        Enviar backup a un solo número de Telegram.
        Lee TELEGRAM_TOKEN y TELEGRAM_CHAT_ID_BACKUP del .env.
        """
        # --- Leer variables del .env (nombres reales del proyecto) ---
        token = self._obtener_configuracion_env("TELEGRAM_TOKEN")
        numero_backup = self._obtener_configuracion_env("TELEGRAM_CHAT_ID_BACKUP")
        habilitado_env = self._obtener_configuracion_env("TELEGRAM_HABILITADO", "false")

        # Si no hay variables de entorno, caer a base de datos
        if not token:
            token = Configuracion.obtener_telegram_token(db)
        if not numero_backup:
            numero_backup = Configuracion.obtener_telegram_backup(db)

        # Si hay token y número de backup en .env, habilitado automáticamente
        if habilitado_env.lower() not in ("true", "1", "si", "yes"):
            if token and numero_backup:
                habilitado_env = "true"
            else:
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

        resultado = await self._enviar_mensaje_individual(token, numero_backup, mensaje)
        if resultado:
            logger.info(f"✅ Backup enviado a {numero_backup}")
        else:
            logger.error(f"❌ Error enviando backup a {numero_backup}")
        return resultado
    
    async def verificar_conexion(self, db: Session) -> dict:
        """
        Verificar la conexión con Telegram.
        Leo TELEGRAM_TOKEN del .env.
        """
        token = self._obtener_configuracion_env("TELEGRAM_TOKEN")
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