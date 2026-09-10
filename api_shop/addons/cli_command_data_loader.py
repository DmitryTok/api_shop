from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from currencies.models import Currency
from discounts.models import Discount
from sizes.models import Size

from api_shop.addons.slugify import generate_unique_slug

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


class DataLoader:
    def __init__(self, stdout=None, style=None):
        self.stdout = stdout
        self.style = style

        self.brands_set: dict[str, Brand] = {}
        self.categories_set: dict[str, Category] = {}
        self.colors_set: dict[str, Color] = {}
        self.currencies_set: dict[str, Currency] = {}
        self.discounts_set: dict[str, Discount] = {}
        self.sizes_set: dict[str, Size] = {}

    def _write(self, message: str):
        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(message))

    def _upload_brands(self):
        Brand.objects.bulk_create(
            (
                Brand(
                    name=brand_name,
                    slug=generate_unique_slug(Brand, brand_name),
                )
                for brand_name in BRANDS
            ),
            ignore_conflicts=True,
        )

        self.brands_set = {brand.name: brand for brand in Brand.objects.all()}

        self._write(f"Brands {len(self.brands_set)} loaded successfully")

    def _upload_categories(self):
        categories_to_create = [
            Category(
                name=category_name,
                slug=generate_unique_slug(Category, category_name),
            )
            for category_name in CATEGORIES
        ]

        Category.objects.bulk_create(
            categories_to_create,
            ignore_conflicts=True,
        )

        self.categories_set = {
            category.name: category
            for category in Category.objects.filter(name__in=CATEGORIES.keys())
        }

        subcategories_to_create = [
            Subcategory(
                name=subcategory_name,
                category=self.categories_set[category_name],
                slug=generate_unique_slug(Subcategory, subcategory_name),
            )
            for category_name, subcategory_names in CATEGORIES.items()
            for subcategory_name in subcategory_names
        ]

        Subcategory.objects.bulk_create(
            subcategories_to_create,
            ignore_conflicts=True,
        )

        all_sub_names = [sub for subs in CATEGORIES.values() for sub in subs]
        self.subcategories_set = {
            sub.name: sub for sub in Subcategory.objects.filter(name__in=all_sub_names)
        }

        self._write(f"Categories {len(self.categories_set)} loaded successfully")
        self._write(f"Subcategories {len(self.subcategories_set)} loaded successfully")

    def _upload_colors(self, colors_data: list[dict]):
        pass

    def _upload_currencies(self, currencies_data: list[dict]):
        pass

    def _upload_discounts(self, discounts_data: list[dict]):
        pass

    def _upload_sizes(self, sizes_data: list[dict]):
        pass
