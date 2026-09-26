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
