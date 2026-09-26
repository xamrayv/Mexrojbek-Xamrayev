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
