from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Category, Product

MAX_IMAGE_MB = 5


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        label="Kategoriya",
        queryset=Category.objects.all(),
        required=False,
        empty_label="Kategoriyani tanlang",
    )
    new_category = forms.CharField(
        label="Yoki yangi kategoriya",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Masalan: Televizorlar"}),
        help_text="Kerakli kategoriya ro'yxatda bo'lmasa, nomini shu yerga yozing.",
    )

    field_order = ["title", "category", "new_category", "price", "description", "image", "is_vip"]

    class Meta:
        model = Product
        fields = ["title", "category", "price", "description", "image", "is_vip"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Masalan: iPhone 15 Pro 256 GB"}),
            "price": forms.NumberInput(attrs={"placeholder": "0", "min": 0}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Mahsulot haqida qisqacha..."}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def clean(self):
        cleaned = super().clean()
        new = " ".join((cleaned.get("new_category") or "").split())
        self._existing = None

        if new:
            # Yangi nom yozilgan bo'lsa, u ustun turadi. Shunday kategoriya bor bo'lsa, o'shani ishlatamiz.
            existing = Category.objects.filter(name__iexact=new).first()
            if existing is None and slugify(new):
                existing = Category.objects.filter(slug=slugify(new)).first()
            self._existing = existing
            cleaned["new_category"] = new
        elif not cleaned.get("category"):
            self.add_error("category", "Kategoriyani tanlang yoki yangisini yozing")
        return cleaned

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "size") and image.size > MAX_IMAGE_MB * 1024 * 1024:
            raise ValidationError(f"Rasm hajmi {MAX_IMAGE_MB} MB dan oshmasligi kerak")
        return image

    def save(self, commit=True):
        product = super().save(commit=False)
        new = self.cleaned_data.get("new_category")
        if new:
            product.category = self._existing or Category.objects.create(name=new)
        if commit:
            product.save()
        return product