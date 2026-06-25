from django.core.management.base import BaseCommand
from django.db import transaction

from addons.slugify import generate_unique_slug
from categories.models import Category, Subcategory


CATEGORIES = {
    "Clothing": [
        "Jackets",
        "Coats",
        "Vests",
        "Hoodies & Sweatshirts",
        "Sweaters",
        "T-Shirts",
        "Shirts",
        "Blouses",
        "Pants",
        "Jeans",
        "Shorts",
        "Skirts",
        "Dresses",
        "Sportswear",
        "Underwear",
        "Loungewear",
    ],
    "Shoes": [
        "Sneakers",
        "Running Shoes",
        "Casual Shoes",
        "Boots",
        "Sandals",
        "Slippers",
    ],
    "Accessories": [
        "Bags",
        "Backpacks",
        "Belts",
        "Hats & Caps",
        "Scarves",
        "Gloves",
        "Wallets",
        "Socks",
    ],
}


class Command(BaseCommand):
    help = "Load initial categories and subcategories"

    def handle(self, *args, **options):
        with transaction.atomic():
            self.stdout.write(self.style.SUCCESS("Command started"))

            existing_categories = {
                category.name: category
                for category in Category.objects.all()
            }

            categories_to_create = []

            for category_name in CATEGORIES:
                if category_name not in existing_categories:
                    categories_to_create.append(
                        Category(
                            name=category_name,
                            slug=generate_unique_slug(
                                Category,
                                category_name,
                            ),
                        )
                    )

            Category.objects.bulk_create(categories_to_create)

            categories = {
                category.name: category
                for category in Category.objects.all()
            }

            existing_subcategories = {
                (subcategory.name, subcategory.category_id)
                for subcategory in Subcategory.objects.all()
            }

            subcategories_to_create = []

            for category_name, subcategory_names in CATEGORIES.items():
                category = categories[category_name]

                for subcategory_name in subcategory_names:
                    key = (subcategory_name, category.id)

                    if key not in existing_subcategories:
                        subcategories_to_create.append(
                            Subcategory(
                                name=subcategory_name,
                                category=category,
                                slug=generate_unique_slug(
                                    Subcategory,
                                    subcategory_name,
                                ),
                            )
                        )

            Subcategory.objects.bulk_create(subcategories_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                "Categories and subcategories loaded successfully"
            )
        )