import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ✅ CORREGIDO - usar variable de entorno
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def enviar_mensaje(texto: str):
    """Envía un mensaje a Telegram"""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("⚠️ Telegram no configurado - mensaje no enviado")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")
        return False