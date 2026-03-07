import os
import subprocess
import requests
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID_NOTIFS = os.getenv("TELEGRAM_CHAT_ID") # Puede ser una lista separada por comas "id1,id2"
TELEGRAM_CHAT_ID_BACKUP = os.getenv("TELEGRAM_CHAT_ID_BACKUP") or TELEGRAM_CHAT_ID_NOTIFS # Fallback
DATABASE_URL = os.getenv("DATABASE_URL")

def enviar_notificacion_texto(mensaje: str):
    """Envia texto a todos los IDs configurados."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID_NOTIFS:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    chats = str(TELEGRAM_CHAT_ID_NOTIFS).split(",")
    for chat_id in chats:
        try:
            requests.post(url, data={"chat_id": chat_id.strip(), "text": mensaje})
        except:
            pass

def generar_y_enviar_backup():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID_BACKUP or not DATABASE_URL:
        print("Error Backup: Faltan variables de entorno para Telegram o BD.")
        return

    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Crear carpeta local de Backups
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backups_dir = os.path.join(base_dir, "Backups")
    os.makedirs(backups_dir, exist_ok=True)
    
    backup_file = os.path.join(backups_dir, f"trueno_backup_{fecha_str}.sql.gz")

    try:
        # Notificar inicio a todos
        enviar_notificacion_texto(f"🔄 Iniciando Cierre de Sistema y Backup automático: {fecha_str}")

        # Ejecutar pg_dump y pasarlo por gzip
        comando = f"pg_dump {DATABASE_URL} | gzip > {backup_file}"
        subprocess.run(comando, shell=True, check=True)
        print(f"✅ Backup generado localmente en: {backup_file}")

        # Enviar archivo SOLO al chat de Backups
        url_doc = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        with open(backup_file, "rb") as f:
            respuesta = requests.post(
                url_doc,
                data={"chat_id": str(TELEGRAM_CHAT_ID_BACKUP).strip(), "caption": f"📦 Backup Automatico Trueno Motors\nFecha: {fecha_str}\n\nNota: También se guardó una copia en el equipo local."},
                files={"document": f}
            )

        if respuesta.status_code == 200:
            enviar_notificacion_texto("✅ Backup a la nube completado y guardado.")
        else:
            enviar_notificacion_texto("⚠️ El backup local se creó, pero hubo un error enviándolo a Telegram.")

    except Exception as e:
        enviar_notificacion_texto(f"❌ Error en proceso de backup: {e}")
        print(f"Error general en proceso de backup: {e}")
    # Nota: Ya no eliminamos el archivo, se guarda en local permanentemente.


@router.post("/backup")
def disparar_backup(background_tasks: BackgroundTasks):
    """
    Endpoint para disparar manualmente el backup a Telegram de forma asíncrona.
    """
    background_tasks.add_task(generar_y_enviar_backup)
    return {"mensaje": "Proceso de backup iniciado en segundo plano. Llegará a Telegram pronto."}
