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
