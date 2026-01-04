# services/telegram_service.py
import requests

TELEGRAM_API_URL = "https://api.telegram.org/bot{8578549192:AAF4KOqHPTcYrXphFTFArhP5AeGMEovoYHU}/sendMessage"

def enviar_mensaje(token: str, chat_id: str, mensaje: str):
    url = TELEGRAM_API_URL.format(token=token)

    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        # IMPORTANTE: nunca romper el sistema por una alerta
        print(f"[Telegram ERROR] {e}")