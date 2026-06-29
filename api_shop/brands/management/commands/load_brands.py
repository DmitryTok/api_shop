from django.core.management.base import BaseCommand
from django.db import transaction

from addons.slugify import generate_unique_slug
from brands.models import Brand


BRANDS = [
    "Nike",
    "Adidas",
    "Puma",
    "New Balance",
    "Reebok",
    "Converse",
    "Vans",
    "Tommy Hilfiger",
    "Calvin Klein",
    "Levi's",
]


class Command(BaseCommand):
    help = "Load initial brands"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Command started"))

        brands_to_create = [
            Brand(
                name=brand_name,
                slug=generate_unique_slug(Brand, brand_name),
            )
            for brand_name in BRANDS
        ]

        with transaction.atomic():
            Brand.objects.bulk_create(
                brands_to_create,
                update_conflicts=True,
                update_fields=["slug"],
                unique_fields=["name"],
            )

        self.stdout.write(
            self.style.SUCCESS("Brands loaded successfully")
        )
