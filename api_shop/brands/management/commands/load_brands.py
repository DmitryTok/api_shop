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
        with transaction.atomic():
            self.stdout.write(
                self.style.SUCCESS("Command started")
            )

            existing_brands = {
                brand.name: brand
                for brand in Brand.objects.all()
            }

            brands_to_create = []

            for brand_name in BRANDS:
                if brand_name not in existing_brands:
                    brands_to_create.append(
                        Brand(
                            name=brand_name,
                            slug=generate_unique_slug(
                                Brand,
                                brand_name,
                            ),
                        )
                    )

            Brand.objects.bulk_create(brands_to_create)

            self.stdout.write(
                self.style.SUCCESS(
                    "Brands loaded successfully"
                )
            )
