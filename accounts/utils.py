import re

from django.core.exceptions import ValidationError


def normalize_phone(value):
    """Har xil yozilgan raqamni yagona ko'rinishga keltiradi: +998901234567"""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 10 and digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 9:
        digits = "998" + digits
    if len(digits) != 12 or not digits.startswith("998"):
        raise ValidationError("Telefon raqamni to'g'ri kiriting. Masalan: +998 90 123 45 67")
    return "+" + digits
