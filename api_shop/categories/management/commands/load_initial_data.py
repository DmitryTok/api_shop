from django.core.management.base import BaseCommand

from categories.serializers import (
    CategorySerializer,
    SubcategorySerializer,
)
from brands.serializers import BrandSerializer
from categories.models import Category

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
    help = "Load initial categories, subcategories and brands"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("Command started")
        )

        for category_name in CATEGORIES:
            serializer = CategorySerializer(
                data={"name": category_name}
            )

            if serializer.is_valid():
                serializer.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Category {category_name} created"
                    )
                )

        for category_name, subcategories in CATEGORIES.items():
            category = Category.objects.get(name=category_name)

            for subcategory_name in subcategories:
                serializer = SubcategorySerializer(
                    data={
                        "name": subcategory_name,
                        "category": category.id,
                    }
                )

                if serializer.is_valid():
                    serializer.save()

        for brand_name in BRANDS:
            serializer = BrandSerializer(
                data={"name": brand_name}
            )

            if serializer.is_valid():
                serializer.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Brand {brand_name} created"
                    )
                )
 

        