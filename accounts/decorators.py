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
