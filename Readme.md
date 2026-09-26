# Bozorcha: noldan qurish qo'llanmasi

Telefon + Telegram kod bilan kirish, profil, kategoriyalar, mahsulotlar, VIP bo'limi, qidiruv va qorong'i dizayn.

## A. Eng tez yo'l (zip)

```bash
# zipni oching, papkaga kiring
cd bozorcha
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
python manage.py makemigrations accounts core
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

Brauzerda: http://127.0.0.1:8000

## B. Noldan qo'lda (startproject / startapp bilan)

```bash
mkdir bozorcha
cd bozorcha
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate       # Mac / Linux
pip install django pillow requests

django-admin startproject config .
python manage.py startapp accounts
python manage.py startapp core
```

Endi qo'shimcha papkalarni oching:

```bash
# Windows (cmd)
mkdir accounts\management\commands core\management\commands templates\accounts templates\core static\css static\js

# Mac / Linux
mkdir -p accounts/management/commands core/management/commands templates/accounts templates/core static/css static/js
```

Bo'sh `__init__.py` fayllarini yarating (ichi bo'sh bo'ladi):

```
accounts/management/__init__.py
accounts/management/commands/__init__.py
core/management/__init__.py
core/management/commands/__init__.py
```

Keyin quyidagi har bir faylni **o'z joyiga** joylang (mavjud bo'lsa, ichini butunlay almashtiring). `tests.py` fayllari kerak emas, o'chirib tashlashingiz mumkin.

## Papkalar daraxti

```
bozorcha/
├── manage.py
├── requirements.txt
├── config/            settings.py, urls.py, wsgi.py, asgi.py
├── accounts/          models, forms, views, urls, admin, utils, telegram, decorators
│   └── management/commands/runbot.py
├── core/              models, forms, views, urls, admin, search
│   └── management/commands/seed_categories.py
├── templates/         base.html, _form.html, _card.html, accounts/, core/
└── static/            css/style.css, js/app.js
```

**Muhim:** `templates` va `static` papkalari `manage.py` bilan **yonma-yon** turadi (`config` yoki ilova ichida emas).

## Ishga tushirish tartibi (B yo'li uchun)

Hamma fayllar joylangach, **aynan shu tartibda**:

```bash
python manage.py makemigrations accounts core
python manage.py migrate
python manage.py seed_categories
python manage.py createsuperuser
python manage.py runserver
```

`migrate` dan **oldin** `makemigrations` bo'lishi shart, chunki loyihada o'zimizning `User` modelimiz bor.

## Telegram bot

Token bo'lmasa ham sinash mumkin: kod terminaldagi `runserver` oynasiga chiqadi (faqat DEBUG yoqiq bo'lsa).
Haqiqiy bot uchun @BotFather'dan token oling va **ikkala** terminalda o'rnating:

```bash
# Windows (cmd)
set TELEGRAM_BOT_TOKEN=123456:ABC...
set TELEGRAM_BOT_USERNAME=mening_botim_bot

# Windows (PowerShell)
$env:TELEGRAM_BOT_TOKEN="123456:ABC..."
$env:TELEGRAM_BOT_USERNAME="mening_botim_bot"

# Mac / Linux
export TELEGRAM_BOT_TOKEN=123456:ABC...
export TELEGRAM_BOT_USERNAME=mening_botim_bot
```

So'ng ikkita terminalda: `python manage.py runserver` va `python manage.py runbot`.
Har bir foydalanuvchi botga bir marta kirib `/start` bosadi va raqamini yuboradi.

## Fayllar


### `requirements.txt`

```text
Django>=5.0
Pillow
requests
```

### `.gitignore`

```text
venv/
__pycache__/
*.pyc
db.sqlite3
media/
.env
```

### `manage.py`

```python
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django topilmadi. Virtual muhit yoqilganmi va "
            "'pip install -r requirements.txt' bajarilganmi?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
```

### `config/settings.py`

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Asosiy ---------------------------------------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-only-change-me-before-deploy")
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "accounts",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Foydalanuvchi va kirish ----------------------------------------------
AUTH_USER_MODEL = "accounts.User"
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Til va vaqt -----------------------------------------------------------
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

# --- Statik va media fayllar -----------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Telegram bot ----------------------------------------------------------
# Token va username muhit o'zgaruvchisidan olinadi (kodga yozmang!)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.environ.get("TELEGRAM_BOT_USERNAME", "")
```

### `config/urls.py`

```python
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("core.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### `config/wsgi.py`

```python
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

### `config/asgi.py`

```python
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_asgi_application()
```

### `accounts/apps.py`

```python
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Hisoblar"
```

### `accounts/utils.py`

```python
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
```

### `accounts/models.py`

```python
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .utils import normalize_phone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra):
        if not phone:
            raise ValueError("Telefon raqam kiritilishi shart")
        user = self.model(phone=normalize_phone(phone), **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra)

    def create_superuser(self, phone, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(phone, password, **extra)


class User(AbstractUser):
    username = None
    phone = models.CharField("Telefon raqam", max_length=13, unique=True)
    telegram_id = models.BigIntegerField("Telegram ID", null=True, blank=True, unique=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    @property
    def display_name(self):
        profile = getattr(self, "profile", None)
        if profile and profile.full_name:
            return profile.full_name
        return self.first_name or "Foydalanuvchi"

    def __str__(self):
        return self.phone


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    full_name = models.CharField("Ism va familiya", max_length=100)
    city = models.CharField("Shahar", max_length=60, blank=True)
    bio = models.TextField("O'zingiz haqingizda", max_length=300, blank=True)
    avatar = models.ImageField("Rasm", upload_to="avatars/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profillar"

    def __str__(self):
        return self.full_name
```

### `accounts/decorators.py`

```python
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .models import Profile


def profile_required(view):
    """Kirgan va profili bor foydalanuvchigina o'tadi. Profilsiz bo'lsa, xato chiqadi."""

    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not Profile.objects.filter(user=request.user).exists():
            messages.error(
                request,
                "Avval profil yarating. Profilsiz mahsulot qo'shish, o'chirish va boshqa amallar ishlamaydi.",
            )
            return redirect("profile")
        return view(request, *args, **kwargs)

    return wrapper
```

### `accounts/telegram.py`

```python
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
```

### `accounts/forms.py`

```python
from django import forms
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError

from .models import Profile, User
from .utils import normalize_phone

PHONE_ATTRS = {
    "placeholder": "+998 90 123 45 67",
    "inputmode": "tel",
    "autocomplete": "tel",
}


class LoginForm(forms.Form):
    phone = forms.CharField(
        label="Telefon raqam",
        widget=forms.TextInput(attrs={**PHONE_ATTRS, "autofocus": True}),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean_phone(self):
        return normalize_phone(self.cleaned_data["phone"])

    def clean(self):
        cleaned = super().clean()
        phone, password = cleaned.get("phone"), cleaned.get("password")
        if phone and password:
            self.user = authenticate(self.request, phone=phone, password=password)
            if self.user is None:
                raise ValidationError("Telefon raqam yoki parol noto'g'ri")
        return cleaned


class RegisterForm(forms.ModelForm):
    # Modeldagi max_length=13 formaga o'tmasligi uchun qayta e'lon qilinadi
    phone = forms.CharField(
        label="Telefon raqam",
        max_length=25,
        widget=forms.TextInput(attrs=PHONE_ATTRS),
    )
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Parolni takrorlang",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "phone"]
        labels = {"first_name": "Ismingiz"}

    def clean_phone(self):
        phone = normalize_phone(self.cleaned_data["phone"])
        if User.objects.filter(phone=phone).exists():
            raise ValidationError("Bu raqam bilan hisob allaqachon mavjud")
        return phone

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        password_validation.validate_password(password)
        return password

    def clean_password2(self):
        p1, p2 = self.cleaned_data.get("password1"), self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Parollar bir xil emas")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class VerifyForm(forms.Form):
    code = forms.CharField(
        label="Telegramdan kelgan 6 xonali kod",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
                "placeholder": "000000",
                "autofocus": True,
            }
        ),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            raise ValidationError("Kod faqat raqamlardan iborat bo'lishi kerak")
        return code


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "city", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
            "avatar": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar and hasattr(avatar, "size") and avatar.size > 5 * 1024 * 1024:
            raise ValidationError("Rasm hajmi 5 MB dan oshmasligi kerak")
        return avatar
```

### `accounts/views.py`

```python
import hashlib
import hmac
import secrets
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, ProfileForm, RegisterForm, VerifyForm
from .models import Profile, User
from .telegram import send_message

CODE_TTL = 300          # kod 5 daqiqa amal qiladi
RESEND_COOLDOWN = 60    # qayta yuborish oralig'i (soniya)
MAX_ATTEMPTS = 5        # noto'g'ri urinishlar soni


def _dev_mode():
    """Token yo'q va DEBUG yoqiq bo'lsa, kod Telegramga emas, terminalga chiqadi."""
    return settings.DEBUG and not settings.TELEGRAM_BOT_TOKEN


def _hash_code(code):
    return hmac.new(settings.SECRET_KEY.encode(), code.encode(), hashlib.sha256).hexdigest()


def _safe_next(request, url):
    if url and url_has_allowed_host_and_scheme(url, allowed_hosts={request.get_host()}):
        return url
    return ""


def _send_code(request, user, next_url=""):
    code = f"{secrets.randbelow(10**6):06d}"

    if _dev_mode():
        print(f"\n[DEV] {user.phone} uchun kirish kodi: {code}\n", flush=True)
    else:
        if not user.telegram_id:
            return False
        sent = send_message(
            user.telegram_id,
            f"🔐 Kirish kodi: <b>{code}</b>\n\nKod 5 daqiqa amal qiladi. Uni hech kimga bermang.",
        )
        if not sent:
            return False

    now = time.time()
    request.session["pending_login"] = {
        "uid": user.pk,
        "hash": _hash_code(code),
        "exp": now + CODE_TTL,
        "sent": now,
        "attempts": 0,
        "next": next_url,
    }
    return True


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.user
        if not user.telegram_id and not _dev_mode():
            return render(request, "accounts/telegram_connect.html", {
                "bot_username": settings.TELEGRAM_BOT_USERNAME,
                "from_login": True,
            })
        next_url = _safe_next(request, request.GET.get("next", ""))
        if _send_code(request, user, next_url):
            return redirect("verify")
        form.add_error(None, "Kodni Telegramga yuborib bo'lmadi. Birozdan so'ng qayta urinib ko'ring.")
    return render(request, "accounts/login.html", {"form": form})


def verify_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    pending = request.session.get("pending_login")
    if not pending:
        return redirect("login")

    if time.time() > pending["exp"]:
        request.session.pop("pending_login", None)
        messages.error(request, "Kod muddati tugadi. Qaytadan kiring.")
        return redirect("login")

    form = VerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pending["attempts"] += 1
        if pending["attempts"] > MAX_ATTEMPTS:
            request.session.pop("pending_login", None)
            messages.error(request, "Juda ko'p noto'g'ri urinish. Qaytadan kiring.")
            return redirect("login")

        if hmac.compare_digest(_hash_code(form.cleaned_data["code"]), pending["hash"]):
            user = User.objects.get(pk=pending["uid"])
            next_url = pending.get("next", "")
            request.session.pop("pending_login", None)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect(next_url or "home")

        request.session["pending_login"] = pending  # urinishlar sonini saqlash
        form.add_error("code", "Kod noto'g'ri")

    return render(request, "accounts/verify.html", {"form": form, "dev": _dev_mode()})


@require_POST
def resend_view(request):
    pending = request.session.get("pending_login")
    if not pending:
        return redirect("login")

    wait = RESEND_COOLDOWN - (time.time() - pending["sent"])
    if wait > 0:
        messages.error(request, f"Yangi kodni {int(wait) + 1} soniyadan so'ng so'rang.")
        return redirect("verify")

    user = User.objects.get(pk=pending["uid"])
    if _send_code(request, user, pending.get("next", "")):
        messages.success(request, "Yangi kod yuborildi.")
    else:
        messages.error(request, "Kodni yuborib bo'lmadi.")
    return redirect("verify")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        if _dev_mode():
            messages.success(request, "Hisob yaratildi. Endi kiring.")
            return redirect("login")
        messages.success(request, "Hisob yaratildi. Endi Telegram botni ulang.")
        return redirect("telegram_connect")
    return render(request, "accounts/register.html", {"form": form})


def telegram_connect_view(request):
    return render(request, "accounts/telegram_connect.html", {
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
    })


@login_required
def profile_view(request):
    profile = Profile.objects.filter(user=request.user).first()
    creating = profile is None

    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
        initial={"full_name": request.user.first_name} if creating else None,
    )
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(
            request,
            "Profil yaratildi. Endi mahsulot qo'sha olasiz." if creating else "Profil yangilandi.",
        )
        return redirect("profile")

    return render(request, "accounts/profile.html", {
        "form": form,
        "profile": profile,
        "creating": creating,
        "product_count": request.user.products.count(),
    })
```

### `accounts/urls.py`

```python
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("verify/", views.verify_view, name="verify"),
    path("resend/", views.resend_view, name="resend"),
    path("register/", views.register_view, name="register"),
    path("telegram/", views.telegram_connect_view, name="telegram_connect"),
    path("profile/", views.profile_view, name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
```

### `accounts/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import RegisterForm
from .models import Profile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = RegisterForm
    ordering = ("phone",)
    list_display = ("phone", "first_name", "telegram_id", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("phone", "first_name")
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Shaxsiy", {"fields": ("first_name", "last_name", "email", "telegram_id")}),
        ("Ruxsatlar", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Sanalar", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("first_name", "phone", "password1", "password2")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "city", "created_at")
    search_fields = ("full_name", "user__phone")
```

### `accounts/management/commands/runbot.py`

```python
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
                updates = r.json().get("result", [])
            except (requests.RequestException, ValueError):
                time.sleep(3)
                continue

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
```

### `core/apps.py`

```python
from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Do'kon"
```

### `core/models.py`

```python
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("Nomi", max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField("Nomi", max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Kategoriya"
    )
    price = models.PositiveIntegerField("Narxi (so'm)")
    description = models.TextField("Tavsif")
    image = models.ImageField("Rasm", upload_to="products/%Y/%m/")
    is_vip = models.BooleanField(
        "Targ'ib qilinsin",
        default=True,
        help_text="Yoqilsa, mahsulot kategoriyada targ'ib qilinadi. O'chirilsa, VIP bo'limida saqlanadi.",
    )
    created_at = models.DateTimeField("Qo'shilgan sana", auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products", verbose_name="Muallif"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def delete(self, *args, **kwargs):
        image = self.image
        result = super().delete(*args, **kwargs)
        if image:
            image.delete(save=False)  # rasm faylini ham o'chiradi
        return result

    def __str__(self):
        return self.title
```

### `core/forms.py`

```python
from django import forms
from django.core.exceptions import ValidationError

from .models import Product

MAX_IMAGE_MB = 5


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["title", "category", "price", "description", "image", "is_vip"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Masalan: iPhone 15 Pro 256 GB"}),
            "price": forms.NumberInput(attrs={"placeholder": "0", "min": 0}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Mahsulot haqida qisqacha..."}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size") and image.size > MAX_IMAGE_MB * 1024 * 1024:
            raise ValidationError(f"Rasm hajmi {MAX_IMAGE_MB} MB dan oshmasligi kerak")
        return image
```

### `core/search.py`

```python
import re
from difflib import SequenceMatcher


def score(query, text):
    """0 = mos emas. Qancha katta bo'lsa, shuncha o'xshash."""
    q = query.casefold().strip()
    t = text.casefold()
    if not q:
        return 0
    if t == q:
        return 100
    if t.startswith(q):
        return 90
    if q in t:
        return 80
    words = [w for w in re.split(r"\W+", t) if w] + [t]
    best = max(SequenceMatcher(None, q, w).ratio() for w in words)
    return int(best * 70) if best >= 0.6 else 0


def rank(items, query, key):
    """(mos kelganlar, qolganlar) qaytaradi. Mos kelganlar o'xshashligi bo'yicha tartiblanadi."""
    scored = [(score(query, key(i)), i) for i in items]
    hits = sorted((x for x in scored if x[0] > 0), key=lambda x: -x[0])
    matched = [i for _, i in hits]
    rest = [i for s, i in scored if s == 0]
    for i in matched:
        i.hit = True
    return matched, rest
```

### `core/views.py`

```python
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.decorators import profile_required

from .forms import ProductForm
from .models import Category, Product
from .search import rank


def _products():
    return Product.objects.select_related("category", "author__profile")


def _own_products(user):
    """Admin hammasini, oddiy foydalanuvchi faqat o'zinikini ko'radi."""
    qs = _products()
    return qs if user.is_staff else qs.filter(author=user)


@login_required
def home(request):
    q = request.GET.get("q", "").strip()[:60]
    categories = list(Category.objects.all())
    products = _products().filter(is_vip=True)
    current = None
    found = 0

    slug = request.GET.get("category")
    if slug:
        current = get_object_or_404(Category, slug=slug)
        products = list(products.filter(category=current))
        if q:
            matched, rest = rank(products, q, lambda p: p.title)
            products = matched + rest
            found = len(matched)
    else:
        products = list(products)
        if q:
            matched, rest = rank(categories, q, lambda c: c.name)
            categories = matched + rest
            found = len(matched)

    return render(request, "core/home.html", {
        "categories": categories,
        "products": products,
        "current": current,
        "q": q,
        "found": found,
    })


@profile_required
def my_categories(request):
    categories = (
        Category.objects.filter(products__author=request.user)
        .annotate(n=Count("products"))
    )
    total = Product.objects.filter(author=request.user).count()
    return render(request, "core/mine_categories.html", {"categories": categories, "total": total})


@profile_required
def my_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _products().filter(author=request.user, category=category)
    return render(request, "core/mine_products.html", {"category": category, "products": products})


@profile_required
def vip_view(request):
    products = _own_products(request.user).filter(is_vip=False)

    if request.method == "POST":
        ids = [i for i in request.POST.getlist("products") if i.isdigit()]
        if ids:
            count = Product.objects.filter(pk__in=products.filter(pk__in=ids).values("pk")).update(is_vip=True)
            messages.success(request, f"{count} ta mahsulot kategoriyasiga qo'shildi.")
        else:
            messages.error(request, "Avval mahsulotni belgilang.")
        return redirect("vip")

    return render(request, "core/vip.html", {"products": products})


@profile_required
def product_add(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.author = request.user
        product.save()
        if product.is_vip:
            messages.success(request, "Mahsulot qo'shildi va targ'ib qilinmoqda.")
            return redirect(f"{reverse('home')}?category={product.category.slug}")
        messages.success(request, "Mahsulot VIP bo'limiga saqlandi.")
        return redirect("vip")
    return render(request, "core/product_form.html", {"form": form})


@profile_required
def delete_categories(request):
    return render(request, "core/delete_categories.html", {"categories": Category.objects.all()})


@profile_required
def delete_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = _own_products(request.user).filter(category=category)
    return render(request, "core/delete_products.html", {"category": category, "products": products})


@profile_required
def product_delete(request, pk):
    product = get_object_or_404(_own_products(request.user), pk=pk)
    if request.method == "POST":
        category = product.category
        title = product.title
        product.delete()
        messages.success(request, f"«{title}» o'chirildi.")
        return redirect("delete_products", slug=category.slug)
    return render(request, "core/product_confirm_delete.html", {"product": product})
```

### `core/urls.py`

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("mine/", views.my_categories, name="my_categories"),
    path("mine/<slug:slug>/", views.my_products, name="my_products"),
    path("vip/", views.vip_view, name="vip"),
    path("add/", views.product_add, name="product_add"),
    path("delete/", views.delete_categories, name="delete_categories"),
    path("delete/<slug:slug>/", views.delete_products, name="delete_products"),
    path("product/<int:pk>/delete/", views.product_delete, name="product_delete"),
]
```

### `core/admin.py`

```python
from django.contrib import admin

from .models import Category, Product

admin.site.site_header = "Bozorcha boshqaruvi"
admin.site.site_title = "Bozorcha"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "is_vip", "author", "created_at")
    list_filter = ("category", "is_vip")
    search_fields = ("title",)
    raw_id_fields = ("author",)
```

### `core/management/commands/seed_categories.py`

```python
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Category

NAMES = ["Telefonlar", "Noutbuklar", "Maishiy texnika", "Kiyim-kechak", "Aksessuarlar"]


class Command(BaseCommand):
    help = "Standart kategoriyalarni yaratadi"

    def handle(self, *args, **options):
        for name in NAMES:
            _, created = Category.objects.get_or_create(slug=slugify(name), defaults={"name": name})
            self.stdout.write(f"{'yaratildi' if created else 'bor'}: {name}")
```

### `templates/base.html`

```html
{% load static %}<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <meta name="theme-color" content="#0d1220">
  <title>{% block title %}Bosh sahifa{% endblock %} - Bozorcha</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  <script src="{% static 'js/app.js' %}" defer></script>
</head>
<body>

<!-- Ikonkalar (bir marta e'lon qilinadi, hamma joyda <use> bilan ishlatiladi) -->
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="i-home" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></symbol>
  <symbol id="i-box" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8 12 3 3 8v8l9 5 9-5zM3 8l9 5 9-5M12 13v8"/></symbol>
  <symbol id="i-star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z"/></symbol>
  <symbol id="i-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-trash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></symbol>
  <symbol id="i-search" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></symbol>
  <symbol id="i-logout" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h4M16 17l5-5-5-5M21 12H9"/></symbol>
  <symbol id="i-cal" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></symbol>
  <symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 5 5 9-9"/></symbol>
  <symbol id="i-back" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M11 6l-6 6 6 6"/></symbol>
  <symbol id="i-chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 6 6 6-6 6"/></symbol>
  <symbol id="i-zap" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></symbol>
  <symbol id="i-phone" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/></symbol>
  <symbol id="i-pin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></symbol>
  <symbol id="i-alert" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4 2.5 20h19zM12 10v4M12 17.5v.01"/></symbol>
  <symbol id="i-image" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="m21 16-5-5-8 8"/></symbol>
</svg>

{% with n=request.resolver_match.url_name %}
<header class="bar">
  <div class="bar-in">
    <a class="brand" href="{% url 'home' %}"><span class="mark">B</span>Bozorcha</a>

    {% if user.is_authenticated %}
      <nav class="tabs" aria-label="Asosiy menyu">
        <a class="tab{% if n == 'home' %} on{% endif %}" href="{% url 'home' %}"><svg class="i"><use href="#i-home"/></svg>Bosh sahifa</a>
        <a class="tab{% if n == 'my_categories' or n == 'my_products' %} on{% endif %}" href="{% url 'my_categories' %}"><svg class="i"><use href="#i-box"/></svg>Men qo'shganlar</a>
        <a class="tab{% if n == 'vip' %} on{% endif %}" href="{% url 'vip' %}"><svg class="i"><use href="#i-star"/></svg>VIP</a>
        <a class="tab danger{% if n == 'delete_categories' or n == 'delete_products' or n == 'product_delete' %} on{% endif %}" href="{% url 'delete_categories' %}"><svg class="i"><use href="#i-trash"/></svg>O'chirish</a>
      </nav>
      <div class="actions">
        <a class="btn primary" href="{% url 'product_add' %}"><svg class="i"><use href="#i-plus"/></svg>Qo'shish</a>
        <a class="me" href="{% url 'profile' %}" title="Profil">
          <span class="ava">{% if user.profile.avatar %}<img src="{{ user.profile.avatar.url }}" alt="">{% else %}{{ user.display_name|first|upper }}{% endif %}</span>
          <span class="nm">{{ user.display_name }}</span>
        </a>
        <form method="post" action="{% url 'logout' %}">
          {% csrf_token %}
          <button class="btn icon ghost" type="submit" title="Chiqish" aria-label="Chiqish"><svg class="i"><use href="#i-logout"/></svg></button>
        </form>
      </div>
    {% endif %}
  </div>
</header>

<main class="wrap{% block wrapclass %}{% endblock %}">
  {% if user.is_authenticated and not user.profile and n != 'profile' %}
    <div class="notice">
      <svg class="i"><use href="#i-alert"/></svg>
      <span>Profil yaratilmagan. Mahsulot qo'shish va boshqa amallar uchun avval <a href="{% url 'profile' %}">profil yarating</a>.</span>
    </div>
  {% endif %}
  {% block content %}{% endblock %}
</main>
{% endwith %}

<div class="toasts" aria-live="polite">
  {% for m in messages %}<div class="toast {{ m.tags }}">{{ m }}</div>{% endfor %}
</div>

<!-- O'chirishni tasdiqlash oynasi -->
<dialog id="confirm" class="modal">
  <form method="post" id="confirm-form">
    {% csrf_token %}
    <h3>Rostdan ham o'chirmoqchimisiz?</h3>
    <p id="confirm-text"></p>
    <div class="row">
      <button class="btn ghost" type="button" data-close>Yo'q</button>
      <button class="btn solid-danger" type="submit">Ha, o'chirish</button>
    </div>
  </form>
</dialog>

</body>
</html>
```

### `templates/_form.html`

```html
{% for e in form.non_field_errors %}<div class="alert err">{{ e }}</div>{% endfor %}
{% for f in form.hidden_fields %}{{ f }}{% endfor %}
<div class="fields{% if cols %} cols{% endif %}">
  {% for field in form.visible_fields %}
    {% if field.field.widget.input_type == "checkbox" %}
      <div>
        <label class="switch">
          {{ field }}
          <span class="track"></span>
          <span class="switch-text">
            <b>{{ field.label }}</b>
            {% if field.help_text %}<small>{{ field.help_text }}</small>{% endif %}
          </span>
        </label>
        {% for e in field.errors %}<p class="err">{{ e }}</p>{% endfor %}
      </div>
    {% else %}
      <div class="field">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}
        {% if field.help_text %}<small class="hint">{{ field.help_text }}</small>{% endif %}
        {% for e in field.errors %}<p class="err">{{ e }}</p>{% endfor %}
      </div>
    {% endif %}
  {% endfor %}
</div>
```

### `templates/_card.html`

```html
{% load humanize %}
<article class="card{% if p.hit %} hit{% endif %}">
  <div class="media">
    <img src="{{ p.image.url }}" alt="{{ p.title }}" loading="lazy">
    <span class="pill">{{ p.category.name }}</span>
    {% if p.is_vip %}
      <span class="flag"><svg class="i"><use href="#i-zap"/></svg>Targ'ib</span>
    {% elif mode == "mine" %}
      <span class="flag muted"><svg class="i"><use href="#i-star"/></svg>VIP bo'limida</span>
    {% endif %}
    {% if mode == "select" %}
      <label class="pick" title="Belgilash">
        <input type="checkbox" name="products" value="{{ p.pk }}">
        <span class="box"><svg class="i"><use href="#i-check"/></svg></span>
      </label>
    {% endif %}
  </div>
  <div class="body">
    <h3 title="{{ p.title }}">{{ p.title }}</h3>
    <p class="desc">{{ p.description }}</p>
    <div class="buy">
      <span class="price">{{ p.price|intcomma }} <small>so'm</small></span>
      {% if mode == "delete" %}
        <a class="btn danger sm" href="{% url 'product_delete' p.pk %}"
           data-confirm-url="{% url 'product_delete' p.pk %}"
           data-confirm-text="«{{ p.title }}» butunlay o'chiriladi.">
          <svg class="i"><use href="#i-trash"/></svg>O'chirish
        </a>
      {% endif %}
    </div>
  </div>
  <footer class="meta">
    <span title="{{ p.created_at|date:'d.m.Y H:i' }}"><svg class="i"><use href="#i-cal"/></svg>{{ p.created_at|date:"d.m.Y" }}</span>
    <span><span class="mini">{{ p.author.display_name|first|upper }}</span>{{ p.author.display_name }}</span>
  </footer>
</article>
```

### `templates/accounts/login.html`

```html
{% extends "base.html" %}
{% block title %}Kirish{% endblock %}
{% block wrapclass %} narrow{% endblock %}
{% block content %}
<div class="auth">
  <div class="auth-head">
    <h1>Hisobga kirish</h1>
    <p class="sub">Telefon raqam va parolingizni kiriting. Tasdiqlash kodi Telegramga yuboriladi.</p>
  </div>
  <form method="post" class="panel">
    {% csrf_token %}
    {% include "_form.html" %}
    <button class="btn primary block" type="submit">Kirish</button>
  </form>
  <div class="divider">Hisobingiz yo'qmi?</div>
  <a class="btn block" href="{% url 'register' %}"><svg class="i"><use href="#i-plus"/></svg>Hisob yaratish</a>
</div>
{% endblock %}
```

### `templates/accounts/register.html`

```html
{% extends "base.html" %}
{% block title %}Hisob yaratish{% endblock %}
{% block wrapclass %} narrow{% endblock %}
{% block content %}
<div class="auth">
  <div class="auth-head">
    <h1>Hisob yaratish</h1>
    <p class="sub">Telefon raqamingiz orqali tizimga kirasiz.</p>
  </div>
  <form method="post" class="panel">
    {% csrf_token %}
    {% include "_form.html" %}
    <button class="btn primary block" type="submit">Ro'yxatdan o'tish</button>
  </form>
  <p class="auth-alt">Hisobingiz bormi? <a href="{% url 'login' %}">Kirish</a></p>
</div>
{% endblock %}
```

### `templates/accounts/verify.html`

```html
{% extends "base.html" %}
{% block title %}Tasdiqlash{% endblock %}
{% block wrapclass %} narrow{% endblock %}
{% block content %}
<div class="auth">
  <div class="auth-head">
    <h1>Kodni kiriting</h1>
    {% if dev %}
      <p class="sub">Telegram token o'rnatilmagan, shuning uchun kod <b>terminalda</b> (runserver oynasida) chiqdi.</p>
    {% else %}
      <p class="sub">6 xonali kod Telegram botingizga yuborildi.</p>
    {% endif %}
  </div>
  <form method="post" class="panel">
    {% csrf_token %}
    <div class="code">{% include "_form.html" %}</div>
    <button class="btn primary block" type="submit">Tasdiqlash</button>
  </form>
  <form method="post" action="{% url 'resend' %}">
    {% csrf_token %}
    <button class="btn ghost block" type="submit">Kod kelmadimi? Qayta yuborish</button>
  </form>
</div>
{% endblock %}
```

### `templates/accounts/telegram_connect.html`

```html
{% extends "base.html" %}
{% block title %}Telegramni ulash{% endblock %}
{% block wrapclass %} narrow{% endblock %}
{% block content %}
<div class="auth">
  <div class="auth-head">
    <h1>Telegram botni ulang</h1>
    <p class="sub">Kirish kodlari Telegram bot orqali yuboriladi. Buni bir marta qilasiz.</p>
  </div>
  <div class="panel">
    <ol class="steps">
      <li>Pastdagi tugma orqali botni oching</li>
      <li><b>Start</b> tugmasini bosing</li>
      <li>«Raqamni yuborish» tugmasini bosing</li>
    </ol>
    {% if bot_username %}
      <a class="btn primary block" href="https://t.me/{{ bot_username }}" target="_blank" rel="noopener">Botni ochish</a>
    {% else %}
      <p class="err">Bot username sozlanmagan (TELEGRAM_BOT_USERNAME).</p>
    {% endif %}
  </div>
  <div class="divider">Ulab bo'lgach</div>
  <a class="btn block" href="{% url 'login' %}">Kirishga qaytish</a>
</div>
{% endblock %}
```

### `templates/accounts/profile.html`

```html
{% extends "base.html" %}
{% block title %}Profil{% endblock %}
{% block content %}
<div class="head first">
  <h1>{% if creating %}Profil yaratish{% else %}Mening profilim{% endif %}</h1>
</div>

<div class="split">
  <aside class="panel who">
    <span class="ava">{% if profile and profile.avatar %}<img src="{{ profile.avatar.url }}" alt="">{% else %}{{ user.display_name|first|upper }}{% endif %}</span>
    <h2>{{ user.display_name }}</h2>
    <span class="row-i"><svg class="i"><use href="#i-phone"/></svg>{{ user.phone }}</span>
    {% if profile and profile.city %}<span class="row-i"><svg class="i"><use href="#i-pin"/></svg>{{ profile.city }}</span>{% endif %}
    {% if profile and profile.bio %}<p class="note">{{ profile.bio }}</p>{% endif %}
    {% if not creating %}
      <a class="btn block" href="{% url 'my_categories' %}"><svg class="i"><use href="#i-box"/></svg>{{ product_count }} ta mahsulot</a>
    {% endif %}
  </aside>

  <form method="post" enctype="multipart/form-data" class="panel">
    {% csrf_token %}
    {% if creating %}
      <p class="notice"><svg class="i"><use href="#i-alert"/></svg><span>Mahsulot qo'shish uchun avval profilni to'ldiring.</span></p>
    {% endif %}
    {% include "_form.html" %}
    <div class="form-actions">
      <button class="btn primary" type="submit">{% if creating %}Profilni yaratish{% else %}Saqlash{% endif %}</button>
    </div>
  </form>
</div>
{% endblock %}
```

### `templates/core/home.html`

```html
{% extends "base.html" %}
{% block title %}Bosh sahifa{% endblock %}
{% block content %}
<form class="search" method="get" action="{% url 'home' %}" role="search">
  {% if current %}<input type="hidden" name="category" value="{{ current.slug }}">{% endif %}
  <svg class="i"><use href="#i-search"/></svg>
  <input type="search" name="q" value="{{ q }}" maxlength="60" aria-label="Qidirish"
         placeholder="{% if current %}{{ current.name }} ichidan mahsulot qidirish{% else %}Kategoriya qidirish{% endif %}">
  {% if q %}<a class="clear" href="{% if current %}{% url 'home' %}?category={{ current.slug }}{% else %}{% url 'home' %}{% endif %}">Tozalash</a>{% endif %}
  <button class="btn primary" type="submit">Qidirish</button>
</form>

<nav class="chips" aria-label="Kategoriyalar">
  <a class="chip{% if not current %} on{% endif %}" href="{% url 'home' %}">Hammasi</a>
  {% for c in categories %}
    <a class="chip{% if current and current.pk == c.pk %} on{% elif c.hit %} hit{% endif %}" href="{% url 'home' %}?category={{ c.slug }}">{{ c.name }}</a>
  {% empty %}
    <span class="note">Kategoriyalar yo'q. Terminalda <code>python manage.py seed_categories</code> ni ishga tushiring.</span>
  {% endfor %}
</nav>

{% if q %}
  <p class="note">
    {% if found %}«{{ q }}» ga mos {{ found }} ta {% if current %}mahsulot{% else %}kategoriya{% endif %} topildi, ular birinchi turibdi.
    {% else %}«{{ q }}» ga o'xshash {% if current %}mahsulot{% else %}kategoriya{% endif %} topilmadi.{% endif %}
  </p>
{% endif %}

<div class="head">
  <h2>{% if current %}{{ current.name }}{% else %}Mahsulotlar{% endif %}</h2>
  <span class="count">{{ products|length }} ta</span>
</div>

{% if products %}
  <div class="grid">
    {% for product in products %}{% include "_card.html" with p=product %}{% endfor %}
  </div>
{% else %}
  <div class="empty">
    <svg class="i"><use href="#i-box"/></svg>
    <p>Bu yerda hozircha mahsulot yo'q.</p>
    <a class="btn primary sm" href="{% url 'product_add' %}"><svg class="i"><use href="#i-plus"/></svg>Mahsulot qo'shish</a>
  </div>
{% endif %}
{% endblock %}
```

### `templates/core/product_form.html`

```html
{% extends "base.html" %}
{% block title %}Mahsulot qo'shish{% endblock %}
{% block wrapclass %} mid{% endblock %}
{% block content %}
<div class="head first"><h1>Yangi mahsulot</h1></div>
<form method="post" enctype="multipart/form-data" class="panel">
  {% csrf_token %}
  {% include "_form.html" with cols=True %}
  <div class="form-actions">
    <button class="btn primary" type="submit">Saqlash</button>
    <a class="btn ghost" href="{% url 'home' %}">Bekor qilish</a>
  </div>
</form>
{% endblock %}
```

### `templates/core/vip.html`

```html
{% extends "base.html" %}
{% block title %}VIP{% endblock %}
{% block content %}
<div class="head first">
  <div>
    <h1>VIP</h1>
    <p class="sub">Targ'ib qilinmayotgan mahsulotlar shu yerda saqlanadi. Kategoriyaga qaytarish uchun belgilang.</p>
  </div>
  <span class="count">{{ products|length }} ta</span>
</div>

{% if products %}
  <form method="post">
    {% csrf_token %}
    <div class="grid">
      {% for product in products %}{% include "_card.html" with p=product mode="select" %}{% endfor %}
    </div>
    <div class="dock">
      <button class="btn primary" type="submit"><svg class="i"><use href="#i-check"/></svg>Belgilanganlarni kategoriyaga qo'shish</button>
    </div>
  </form>
{% else %}
  <div class="empty">
    <svg class="i"><use href="#i-star"/></svg>
    <p>VIP bo'limi bo'sh.</p>
  </div>
{% endif %}
{% endblock %}
```

### `templates/core/mine_categories.html`

```html
{% extends "base.html" %}
{% block title %}Men qo'shganlar{% endblock %}
{% block content %}
<div class="head first">
  <div>
    <h1>Men qo'shganlar</h1>
    <p class="sub">Jami {{ total }} ta mahsulot. Kategoriyani tanlang.</p>
  </div>
</div>

{% if categories %}
  <div class="tiles">
    {% for c in categories %}
      <a class="tile" href="{% url 'my_products' c.slug %}">
        <span>{{ c.name }}<small>{{ c.n }} ta mahsulot</small></span>
        <svg class="i"><use href="#i-chev"/></svg>
      </a>
    {% endfor %}
  </div>
{% else %}
  <div class="empty">
    <svg class="i"><use href="#i-box"/></svg>
    <p>Siz hali mahsulot qo'shmagansiz.</p>
    <a class="btn primary sm" href="{% url 'product_add' %}"><svg class="i"><use href="#i-plus"/></svg>Birinchi mahsulotni qo'shish</a>
  </div>
{% endif %}
{% endblock %}
```

### `templates/core/mine_products.html`

```html
{% extends "base.html" %}
{% block title %}{{ category.name }}{% endblock %}
{% block content %}
<div class="toolbar">
  <a class="btn sm" href="{% url 'my_categories' %}"><svg class="i"><use href="#i-back"/></svg>Kategoriyalar</a>
</div>
<div class="head first">
  <h1>{{ category.name }}</h1>
  <span class="count">{{ products|length }} ta</span>
</div>

{% if products %}
  <div class="grid">
    {% for product in products %}{% include "_card.html" with p=product mode="mine" %}{% endfor %}
  </div>
{% else %}
  <div class="empty"><svg class="i"><use href="#i-box"/></svg><p>Bu kategoriyada sizning mahsulotingiz yo'q.</p></div>
{% endif %}
{% endblock %}
```

### `templates/core/delete_categories.html`

```html
{% extends "base.html" %}
{% block title %}O'chirish{% endblock %}
{% block content %}
<div class="head first">
  <div>
    <h1>Mahsulotni o'chirish</h1>
    <p class="sub">Avval kategoriyani tanlang.</p>
  </div>
</div>

<div class="tiles del">
  {% for c in categories %}
    <a class="tile" href="{% url 'delete_products' c.slug %}"><span>{{ c.name }}</span><svg class="i"><use href="#i-chev"/></svg></a>
  {% empty %}
    <p class="note">Kategoriyalar yo'q.</p>
  {% endfor %}
</div>
{% endblock %}
```

### `templates/core/delete_products.html`

```html
{% extends "base.html" %}
{% block title %}{{ category.name }} - o'chirish{% endblock %}
{% block content %}
<div class="toolbar">
  <a class="btn sm" href="{% url 'delete_categories' %}"><svg class="i"><use href="#i-back"/></svg>Kategoriyalar</a>
</div>
<div class="head first">
  <h1>{{ category.name }}</h1>
  <span class="count">{{ products|length }} ta</span>
</div>

{% if products %}
  <div class="grid">
    {% for product in products %}{% include "_card.html" with p=product mode="delete" %}{% endfor %}
  </div>
{% else %}
  <div class="empty"><svg class="i"><use href="#i-trash"/></svg><p>Bu kategoriyada o'chiriladigan mahsulot yo'q.</p></div>
{% endif %}
{% endblock %}
```

### `templates/core/product_confirm_delete.html`

```html
{% extends "base.html" %}
{% block title %}Tasdiqlash{% endblock %}
{% block wrapclass %} narrow{% endblock %}
{% block content %}
<form method="post" class="panel auth">
  {% csrf_token %}
  <h1>Rostdan ham o'chirmoqchimisiz?</h1>
  <p class="sub">«{{ product.title }}» ({{ product.category.name }}) butunlay o'chiriladi.</p>
  <div class="form-actions" style="margin:0">
    <button class="btn solid-danger" type="submit">Ha, o'chirish</button>
    <a class="btn ghost" href="{% url 'delete_products' product.category.slug %}">Yo'q</a>
  </div>
</form>
{% endblock %}
```

### `static/css/style.css`

```css
/* ==========================================================================
   Bozorcha - qorong'i mavzu
   Ranglar: ko'k-siyoh fon, ko'k tugmalar, sariq (VIP), qizil (o'chirish)
   ========================================================================== */
:root {
  --bg: #0d1220;
  --panel: #151c31;
  --raised: #1c2542;
  --field: #0f1527;
  --line: #2a3555;
  --line-2: #1f2843;
  --text: #e8ecf6;
  --muted: #93a0bd;
  --faint: #66739a;
  --blue: #6b8cff;
  --violet: #8a7dff;
  --amber: #f5b942;
  --green: #3fcf8e;
  --red: #ff6b7b;
  --r: 12px;
  --r-lg: 16px;
  --font: "Manrope", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color-scheme: dark;
}

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  min-height: 100vh;
  font: 500 14.5px/1.5 var(--font);
  color: var(--text);
  background: radial-gradient(900px 380px at 85% -120px, rgba(107, 140, 255, .14), transparent 70%), var(--bg);
  background-attachment: fixed;
}
a { color: inherit; text-decoration: none; }
img { max-width: 100%; }
h1, h2, h3 { margin: 0; line-height: 1.2; letter-spacing: -.01em; }
h1 { font-size: 22px; font-weight: 800; }
h2 { font-size: 17px; font-weight: 700; }
h3 { font-size: 15px; font-weight: 700; }
p { margin: 0; }
:focus-visible { outline: 2px solid var(--blue); outline-offset: 2px; }

.i { width: 16px; height: 16px; flex: none; vertical-align: -3px; }

/* ---------- Yuqori panel ---------- */
.bar {
  position: sticky; top: 0; z-index: 20;
  background: rgba(13, 18, 32, .82);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--line-2);
}
.bar-in {
  max-width: 1120px; margin: 0 auto; padding: 10px 16px;
  display: flex; align-items: center; gap: 14px; flex-wrap: wrap;
}
.brand { display: flex; align-items: center; gap: 9px; font-weight: 800; font-size: 17px; letter-spacing: -.02em; }
.mark {
  width: 28px; height: 28px; border-radius: 9px; display: grid; place-items: center;
  background: linear-gradient(135deg, var(--blue), var(--violet)); color: #fff; font-size: 15px;
}
.tabs { display: flex; gap: 2px; flex: 1; overflow-x: auto; scrollbar-width: none; }
.tabs::-webkit-scrollbar { display: none; }
.tab {
  display: inline-flex; align-items: center; gap: 7px; padding: 7px 12px; border-radius: 9px;
  color: var(--muted); font-weight: 600; font-size: 13.5px; white-space: nowrap;
}
.tab:hover, .tab.on { color: var(--text); background: var(--raised); }
.tab.danger:hover, .tab.danger.on { color: var(--red); }
.actions { display: flex; align-items: center; gap: 8px; }
.actions form { margin: 0; }
.me {
  display: flex; align-items: center; gap: 8px; padding: 3px 12px 3px 3px;
  border-radius: 999px; border: 1px solid var(--line); background: var(--panel);
  font-weight: 700; font-size: 13px;
}
.me:hover { border-color: var(--faint); }
.ava {
  width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; overflow: hidden;
  background: var(--raised); color: var(--muted); font-weight: 800; font-size: 12px; flex: none;
}
.ava img { width: 100%; height: 100%; object-fit: cover; display: block; }
.nm { max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ---------- Sahifa ---------- */
.wrap { max-width: 1120px; margin: 0 auto; padding: 22px 16px 90px; }
.wrap.narrow { max-width: 420px; padding-top: 44px; }
.wrap.mid { max-width: 680px; }

.notice {
  display: flex; gap: 10px; align-items: center; padding: 10px 14px; margin-bottom: 16px;
  border-radius: var(--r); background: rgba(245, 185, 66, .1); border: 1px solid rgba(245, 185, 66, .3);
  color: #f7d488; font-size: 13.5px;
}
.notice a { font-weight: 800; text-decoration: underline; }

.head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin: 22px 0 12px; }
.head.first { margin-top: 0; }
.count { color: var(--faint); font-size: 13px; }
.note { color: var(--muted); font-size: 13px; margin-top: 10px; }
.sub { color: var(--muted); margin-top: 4px; }
.toolbar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }

/* ---------- Tugmalar ---------- */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 7px;
  height: 36px; padding: 0 14px; border-radius: 10px;
  border: 1px solid var(--line); background: var(--raised); color: var(--text);
  font: 700 13.5px var(--font); cursor: pointer; white-space: nowrap;
  transition: background .15s, border-color .15s, filter .15s, color .15s;
}
.btn:hover { border-color: var(--faint); }
.btn.primary { border-color: transparent; background: linear-gradient(135deg, var(--blue), var(--violet)); color: #fff; }
.btn.primary:hover { filter: brightness(1.1); }
.btn.ghost { background: transparent; }
.btn.danger { background: rgba(255, 107, 123, .12); border-color: rgba(255, 107, 123, .35); color: var(--red); }
.btn.danger:hover { background: var(--red); border-color: var(--red); color: #1a0509; }
.btn.solid-danger { background: var(--red); border-color: var(--red); color: #1a0509; }
.btn.solid-danger:hover { filter: brightness(1.1); }
.btn.sm { height: 30px; padding: 0 10px; font-size: 12.5px; border-radius: 8px; }
.btn.icon { width: 36px; padding: 0; }
.btn.block { width: 100%; }

/* ---------- Qidiruv va kategoriyalar ---------- */
.search {
  display: flex; align-items: center; gap: 8px; padding: 5px 5px 5px 14px; margin-bottom: 14px;
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
}
.search:focus-within { border-color: var(--blue); box-shadow: 0 0 0 3px rgba(107, 140, 255, .16); }
.search .i { color: var(--faint); }
.search input {
  flex: 1; min-width: 0; border: 0; background: transparent; color: var(--text);
  font: inherit; padding: 8px 0; outline: 0; -webkit-appearance: none; appearance: none;
}
.search input::placeholder { color: var(--faint); }
.search .clear { color: var(--muted); font-size: 13px; padding: 0 8px; }
.search .clear:hover { color: var(--text); }

.chips { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 6px; scrollbar-width: thin; }
.chip {
  flex: none; padding: 6px 14px; border-radius: 999px; border: 1px solid var(--line);
  background: var(--panel); color: var(--muted); font-weight: 600; font-size: 13.5px;
}
.chip:hover { color: var(--text); border-color: var(--faint); }
.chip.hit { border-color: var(--amber); color: var(--amber); background: rgba(245, 185, 66, .1); }
.chip.on { border-color: transparent; background: linear-gradient(135deg, var(--blue), var(--violet)); color: #fff; }

/* ---------- Mahsulot kartochkasi ---------- */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 14px; }
.card {
  display: flex; flex-direction: column; overflow: hidden;
  background: var(--panel); border: 1px solid var(--line-2); border-radius: var(--r-lg);
  transition: border-color .15s;
}
.card:hover { border-color: var(--line); }
.card.hit { border-color: var(--amber); box-shadow: 0 0 0 1px var(--amber); }
.card:has(.pick input:checked) { border-color: var(--blue); box-shadow: 0 0 0 1px var(--blue); }

.media { position: relative; aspect-ratio: 4 / 3; background: var(--raised); }
.media img { width: 100%; height: 100%; object-fit: cover; display: block; }
.pill, .flag {
  position: absolute; top: 8px; padding: 3px 9px; border-radius: 999px;
  font-size: 11.5px; font-weight: 700; backdrop-filter: blur(6px);
}
.pill { left: 8px; background: rgba(13, 18, 32, .72); color: var(--text); }
.flag { right: 8px; display: inline-flex; align-items: center; gap: 4px; background: var(--amber); color: #2b1d00; }
.flag.muted { background: rgba(13, 18, 32, .72); color: var(--muted); }
.flag .i { width: 12px; height: 12px; }

.pick { position: absolute; inset: 0; cursor: pointer; }
.pick input { position: absolute; inset: 0; width: 100%; height: 100%; margin: 0; opacity: 0; cursor: pointer; }
.pick .box {
  position: absolute; top: 8px; right: 8px; width: 26px; height: 26px; border-radius: 8px;
  display: grid; place-items: center; color: transparent;
  background: rgba(13, 18, 32, .75); border: 1.5px solid var(--muted);
}
.pick input:checked + .box { background: var(--blue); border-color: var(--blue); color: #fff; }
.pick input:focus-visible + .box { outline: 2px solid var(--blue); outline-offset: 2px; }

.body { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 12px 13px 10px; }
.body h3 { font-size: 14.5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.desc {
  color: var(--muted); font-size: 12.5px; line-height: 1.45; min-height: 2.9em;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.buy { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: auto; padding-top: 8px; }
.price { font-weight: 800; font-size: 16px; }
.price small { font-weight: 600; font-size: 12px; color: var(--muted); }
.meta {
  display: flex; justify-content: space-between; gap: 8px; padding: 8px 13px;
  border-top: 1px solid var(--line-2); color: var(--faint); font-size: 12px;
}
.meta span { display: inline-flex; align-items: center; gap: 5px; min-width: 0; }
.meta span:last-child { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta .i { width: 13px; height: 13px; }
.mini {
  width: 16px; height: 16px; border-radius: 50%; display: grid; place-items: center; flex: none;
  background: var(--raised); color: var(--muted); font-size: 9px; font-weight: 800;
}

/* ---------- Kategoriya ro'yxati (Men qo'shganlar / O'chirish) ---------- */
.tiles { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px; }
.tile {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 14px 16px; border-radius: 14px; background: var(--panel); border: 1px solid var(--line-2);
  font-weight: 700;
}
.tile small { display: block; color: var(--muted); font-weight: 600; font-size: 12.5px; margin-top: 2px; }
.tile .i { color: var(--faint); }
.tile:hover { border-color: var(--blue); }
.tiles.del .tile:hover { border-color: var(--red); }

.dock { position: sticky; bottom: 16px; display: flex; justify-content: center; margin-top: 22px; }
.dock .btn { height: 42px; padding: 0 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, .5); }

.empty {
  display: grid; justify-items: center; gap: 10px; text-align: center; padding: 44px 16px;
  border: 1px dashed var(--line); border-radius: var(--r-lg); color: var(--muted);
}
.empty .i { width: 28px; height: 28px; color: var(--faint); }

/* ---------- Panel va formalar ---------- */
.panel { background: var(--panel); border: 1px solid var(--line-2); border-radius: var(--r-lg); padding: 20px; }
.fields { display: grid; gap: 14px; }
.fields.cols { grid-template-columns: 1fr 1fr; }
.fields.cols > * { grid-column: 1 / -1; }
.fields.cols > .field:nth-child(2), .fields.cols > .field:nth-child(3) { grid-column: auto; }
.field { display: grid; gap: 6px; min-width: 0; }
.field label { font-weight: 700; font-size: 13px; color: var(--muted); }
.hint { color: var(--faint); font-size: 12px; }
.err { color: var(--red); font-size: 12.5px; font-weight: 600; }
.alert { padding: 10px 14px; border-radius: var(--r); font-size: 13.5px; font-weight: 600; margin-bottom: 14px; }
.alert.err { background: rgba(255, 107, 123, .1); border: 1px solid rgba(255, 107, 123, .3); }

input:not([type=checkbox]):not([type=file]):not([type=hidden]), select, textarea {
  width: 100%; min-width: 0; padding: 0 12px; height: 40px;
  border: 1px solid var(--line); border-radius: 10px; background: var(--field); color: var(--text);
  font: inherit; transition: border-color .15s, box-shadow .15s;
}
textarea { height: auto; min-height: 90px; padding: 10px 12px; resize: vertical; }
select {
  -webkit-appearance: none; appearance: none; padding-right: 34px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2393a0bd' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 12px center;
}
input::placeholder, textarea::placeholder { color: var(--faint); }
input:focus, select:focus, textarea:focus { outline: 0; border-color: var(--blue); box-shadow: 0 0 0 3px rgba(107, 140, 255, .16); }
input[type=file] {
  width: 100%; padding: 6px; border: 1px dashed var(--line); border-radius: 10px;
  background: var(--field); color: var(--muted); font: inherit; font-size: 13px; cursor: pointer;
}
input[type=file]::file-selector-button {
  margin-right: 12px; padding: 6px 12px; border: 0; border-radius: 8px;
  background: var(--raised); color: var(--text); font: 700 12.5px var(--font); cursor: pointer;
}
.preview { display: block; width: 100%; max-height: 220px; object-fit: cover; border-radius: 10px; margin-top: 8px; }

.switch { position: relative; display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 10px 12px; border: 1px solid var(--line); border-radius: 12px; background: var(--field); }
.switch input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.switch .track { flex: none; width: 38px; height: 22px; border-radius: 999px; background: var(--line); position: relative; transition: background .15s; }
.switch .track::after { content: ""; position: absolute; top: 3px; left: 3px; width: 16px; height: 16px; border-radius: 50%; background: #fff; transition: transform .15s; }
.switch input:checked + .track { background: var(--amber); }
.switch input:checked + .track::after { transform: translateX(16px); }
.switch input:focus-visible + .track { outline: 2px solid var(--blue); outline-offset: 2px; }
.switch-text { display: grid; gap: 2px; }
.switch-text b { font-size: 13.5px; }
.switch-text small { color: var(--faint); font-size: 12px; font-weight: 500; }

.form-actions { display: flex; gap: 8px; margin-top: 18px; flex-wrap: wrap; }

/* ---------- Kirish sahifalari ---------- */
.auth { display: grid; gap: 18px; }
.auth-head { display: grid; gap: 6px; justify-items: start; }
.auth-alt { text-align: center; color: var(--muted); font-size: 13.5px; }
.auth-alt a { color: var(--blue); font-weight: 700; }
.auth .panel { display: grid; gap: 16px; }
.code input { text-align: center; font-size: 26px; font-weight: 800; letter-spacing: .4em; height: 54px; }
.steps { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; counter-reset: s; }
.steps li { display: flex; gap: 10px; align-items: center; counter-increment: s; }
.steps li::before {
  content: counter(s); flex: none; width: 24px; height: 24px; border-radius: 50%;
  display: grid; place-items: center; background: var(--raised); color: var(--blue); font-size: 12px; font-weight: 800;
}
.divider { display: flex; align-items: center; gap: 12px; color: var(--faint); font-size: 12.5px; }
.divider::before, .divider::after { content: ""; flex: 1; height: 1px; background: var(--line-2); }

/* ---------- Profil ---------- */
.split { display: grid; grid-template-columns: 250px 1fr; gap: 16px; align-items: start; }
.who { display: grid; justify-items: center; gap: 4px; text-align: center; }
.who .ava { width: 84px; height: 84px; font-size: 32px; margin-bottom: 8px; }
.who .row-i { display: inline-flex; align-items: center; gap: 6px; color: var(--muted); font-size: 13px; }
.who .btn { margin-top: 12px; }

/* ---------- Tasdiqlash oynasi ---------- */
.modal {
  padding: 0; width: min(92vw, 380px); border: 1px solid var(--line); border-radius: 18px;
  background: var(--panel); color: var(--text); box-shadow: 0 30px 80px rgba(0, 0, 0, .6);
}
.modal::backdrop { background: rgba(5, 8, 16, .72); backdrop-filter: blur(3px); }
.modal[open] { animation: pop .16s ease-out; }
.modal form { padding: 22px; }
.modal p { color: var(--muted); margin: 8px 0 20px; }
.row { display: flex; gap: 8px; justify-content: flex-end; }
@keyframes pop { from { opacity: 0; transform: scale(.96); } }

/* ---------- Xabarlar ---------- */
.toasts { position: fixed; left: 50%; bottom: 20px; transform: translateX(-50%); z-index: 60; display: grid; gap: 8px; width: min(92vw, 420px); pointer-events: none; }
.toast {
  padding: 11px 14px; border-radius: 12px; background: var(--raised); border: 1px solid var(--line);
  border-left: 3px solid var(--blue); box-shadow: 0 12px 30px rgba(0, 0, 0, .45);
  font-weight: 600; font-size: 13.5px; animation: toast 5s forwards;
}
.toast.success { border-left-color: var(--green); }
.toast.error { border-left-color: var(--red); }
@keyframes toast {
  0% { opacity: 0; transform: translateY(10px); }
  6% { opacity: 1; transform: none; }
  88% { opacity: 1; }
  100% { opacity: 0; visibility: hidden; }
}

/* ---------- Mobil ---------- */
@media (max-width: 760px) {
  .split { grid-template-columns: 1fr; }
  .tabs { order: 3; flex: 1 0 100%; }
  .brand { margin-right: auto; }
  .nm { display: none; }
  .me { padding: 3px; }
  .wrap { padding-top: 16px; }
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
  .body { padding: 10px; }
  .meta { padding: 7px 10px; }
  .fields.cols { grid-template-columns: 1fr; }
  .fields.cols > .field:nth-child(2), .fields.cols > .field:nth-child(3) { grid-column: 1 / -1; }
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; }
  .toast, .modal[open] { animation: none; }
}
```

### `static/js/app.js`

```javascript
(() => {
  const dlg = document.getElementById("confirm");
  const form = document.getElementById("confirm-form");
  const text = document.getElementById("confirm-text");

  // O'chirish tugmasi bosilsa, tasdiqlash oynasi ochiladi
  document.addEventListener("click", (e) => {
    const opener = e.target.closest("[data-confirm-url]");
    if (opener && dlg && dlg.showModal) {
      e.preventDefault();
      form.action = opener.dataset.confirmUrl;
      text.textContent = opener.dataset.confirmText || "";
      dlg.showModal();
      return;
    }
    // "Yo'q" tugmasi yoki oyna tashqarisiga bosilsa yopiladi
    if (dlg && (e.target === dlg || e.target.closest("[data-close]"))) dlg.close();
  });

  // Tanlangan rasmni darhol ko'rsatadi
  document.addEventListener("change", (e) => {
    const input = e.target;
    if (input.type !== "file" || !input.files || !input.files[0]) return;
    let img = input.parentElement.querySelector(".preview");
    if (!img) {
      img = document.createElement("img");
      img.className = "preview";
      img.alt = "";
      input.after(img);
    }
    img.src = URL.createObjectURL(input.files[0]);
  });

  // Xabarlar 5 soniyadan so'ng yo'qoladi
  setTimeout(() => document.querySelectorAll(".toast").forEach((t) => t.remove()), 5200);
})();
```

## Ko'p uchraydigan xatolar

| Xato | Sababi va yechimi |
|---|---|
| `no such table` | `migrate` qilinmagan. `makemigrations accounts core`, so'ng `migrate` |
| `AUTH_USER_MODEL refers to model ... not installed` | `accounts` `INSTALLED_APPS` da yo'q |
| `Conflicting/inconsistent migration history` | Eski baza qolgan. `db.sqlite3` va `migrations/` ichidagi `0001_...py` fayllarini o'chirib, qaytadan boshlang |
| `TemplateDoesNotExist` | `templates` papkasi `manage.py` yonida emas |
| CSS ishlamayapti | `static/css/style.css` yo'li tekshiring, `runserver` ni qayta ishga tushiring |
| `ImageField ... Pillow` | `pip install pillow` |
| Kod Telegramga kelmayapti | Bot ulanmagan (`/start` + raqam), `runbot` ishlamayapti yoki token noto'g'ri |
