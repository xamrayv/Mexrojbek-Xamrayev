import requests
from django.conf import settings


def send_message(chat_id, text, reply_markup=None):
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        return False
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json=payload,
            timeout=10,
        )
        return r.ok
    except requests.RequestException:
        return False
