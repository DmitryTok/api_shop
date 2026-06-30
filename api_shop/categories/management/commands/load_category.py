from addons.slugify import generate_unique_slug
from categories.models import Category, Subcategory
from django.core.management.base import BaseCommand
from django.db import transaction

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
        self.stdout.write(self.style.SUCCESS("Command started"))

        categories_to_create = [
            Category(
                name=category_name,
                slug=generate_unique_slug(Category, category_name),
            )
            for category_name in CATEGORIES
        ]

        with transaction.atomic():
            Category.objects.bulk_create(
                categories_to_create,
                update_conflicts=True,
                update_fields=["slug"],
                unique_fields=["name"],
            )

        categories = {
            category.name: category
            for category in Category.objects.filter(name__in=CATEGORIES.keys())
        }

        subcategories_to_create = [
            Subcategory(
                name=subcategory_name,
                category=categories[category_name],
                slug=generate_unique_slug(Subcategory, subcategory_name),
            )
            for category_name, subcategory_names in CATEGORIES.items()
            for subcategory_name in subcategory_names
        ]

        with transaction.atomic():
            Subcategory.objects.bulk_create(
                subcategories_to_create,
                update_conflicts=True,
                update_fields=["slug", "category"],
                unique_fields=["name"],
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Categories and subcategories loaded successfully"
            )
        )
