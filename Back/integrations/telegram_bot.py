import requests
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = f"https://api.telegram.org/bot8578549192:AAF4KOqHPTcYrXphFTFArhP5AeGMEovoYHU"


def enviar_mensaje(texto: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        return

    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML"
    }

    requests.post(f"{BASE_URL}/sendMessage", json=payload)
