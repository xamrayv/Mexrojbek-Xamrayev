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
