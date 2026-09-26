import json
import time

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User
from accounts.telegram import send_message
from accounts.utils import normalize_phone

CONTACT_KEYBOARD = {
    "keyboard": [[{"text": "📱 Raqamni yuborish", "request_contact": True}]],
    "resize_keyboard": True,
    "one_time_keyboard": True,
}


class Command(BaseCommand):
    help = "Telegram botni ishga tushiradi (long polling)"

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise CommandError("TELEGRAM_BOT_TOKEN o'rnatilmagan")

        url = f"https://api.telegram.org/bot{token}/getUpdates"
        offset = None
        self.stdout.write("Bot ishga tushdi. To'xtatish: Ctrl+C")

        while True:
            try:
                r = requests.get(
                    url,
                    params={
                        "timeout": 30,
                        "offset": offset,
                        "allowed_updates": json.dumps(["message"]),
                    },
                    timeout=40,
                )
                data = r.json()
            except (requests.RequestException, ValueError):
                time.sleep(3)
                continue

            if not data.get("ok"):
                self.stderr.write(f"Telegram xatosi: {data.get('description')}")
                time.sleep(5)
                continue

            updates = data.get("result", [])

            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message")
                if message:
                    try:
                        self.handle_message(message)
                    except Exception as exc:  # bitta xato botni to'xtatmasin
                        self.stderr.write(f"Xato: {exc}")

    def handle_message(self, msg):
        if msg["chat"].get("type") != "private":
            return
        chat_id = msg["chat"]["id"]
        contact = msg.get("contact")

        if not contact:
            send_message(
                chat_id,
                "Salom! Hisobingizni ulash uchun pastdagi tugma orqali telefon raqamingizni yuboring.",
                CONTACT_KEYBOARD,
            )
            return

        # Faqat o'zining raqamini yuborishi mumkin
        if contact.get("user_id") != msg["from"]["id"]:
            send_message(chat_id, "Iltimos, o'zingizning raqamingizni yuboring.", CONTACT_KEYBOARD)
            return

        try:
            phone = normalize_phone(contact["phone_number"])
        except ValidationError:
            send_message(chat_id, "Faqat O'zbekiston raqamlari (+998) qo'llab-quvvatlanadi.")
            return

        user = User.objects.filter(phone=phone).first()
        if user is None:
            send_message(chat_id, "Bu raqam bilan hisob topilmadi. Avval saytda hisob yarating, so'ng qaytib keling.")
            return

        User.objects.filter(telegram_id=chat_id).exclude(pk=user.pk).update(telegram_id=None)
        user.telegram_id = chat_id
        user.save(update_fields=["telegram_id"])
        send_message(
            chat_id,
            "✅ Ulandi! Endi saytga kirganingizda tasdiqlash kodi shu yerga keladi.",
            {"remove_keyboard": True},
        )