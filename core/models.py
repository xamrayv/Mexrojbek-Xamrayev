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
            base = slugify(self.name) or "kategoriya"
            slug, n = base, 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
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