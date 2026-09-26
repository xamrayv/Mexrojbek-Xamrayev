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
