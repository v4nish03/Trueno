import os
import subprocess
import requests
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks

router = APIRouter()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")

def generar_y_enviar_backup():
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not DATABASE_URL:
        print("Error Backup: Faltan variables de entorno para Telegram o BD.")
        return

    fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/tmp/trueno_backup_{fecha_str}.sql.gz"

    try:
        # Ejecutar pg_dump y pasarlo por gzip
        # El formato DATABASE_URL de SQLAlchemy es: postgresql://user:pass@host:port/dbname
        # pg_dump lo acepta tal cual
        comando = f"pg_dump {DATABASE_URL} | gzip > {backup_file}"
        subprocess.run(comando, shell=True, check=True)
        print(f"Backup generado localmente en: {backup_file}")

        # Enviar archivo a Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
        
        with open(backup_file, "rb") as f:
            respuesta = requests.post(
                url,
                data={"chat_id": TELEGRAM_CHAT_ID, "caption": f"📦 Backup Automatico Trueno Motors\nFecha: {fecha_str}"},
                files={"document": f}
            )

        if respuesta.status_code == 200:
            print("Backup enviado con exito a Telegram.")
        else:
            print(f"Error enviando backup. Telegram respondio: {respuesta.text}")

    except Exception as e:
        print(f"Error general en proceso de backup: {e}")
    finally:
        # Limpiar archivo temporal para no llenar el disco
        if os.path.exists(backup_file):
            os.remove(backup_file)


@router.post("/backup")
def disparar_backup(background_tasks: BackgroundTasks):
    """
    Endpoint para disparar manualmente el backup a Telegram de forma asíncrona.
    """
    background_tasks.add_task(generar_y_enviar_backup)
    return {"mensaje": "Proceso de backup iniciado en segundo plano. Llegará a Telegram pronto."}
