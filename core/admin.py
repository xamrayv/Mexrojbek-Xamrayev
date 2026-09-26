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
