import os
import random
import time

import psutil
from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from currencies.models import Currency
from discounts.models import Discount
from faker import Faker
from product_variants.models import Gender, ProductVariant
from products.models import Product
from sizes.models import Size

from addons.slugify import generate_unique_slug

FAKE = Faker()

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

COLORS = {
    "Black": "#000000",
    "Blue": "#0000FF",
    "Brown": "#A52A2A",
    "Gray": "#808080",
    "Green": "#008000",
    "Navy": "#000080",
    "Pink": "#FFC0CB",
    "Red": "#FF0000",
    "White": "#FFFFFF",
    "Yellow": "#FFFF00",
}

SIZES = {
    "S": "clothing",
    "M": "clothing",
    "L": "clothing",
    "41 EU": "shoes",
    "42 EU": "shoes",
    "XS": "clothing",
    "XL": "clothing",
    "XXL": "clothing",
    "39 EU": "shoes",
    "40 EU": "shoes",
    "44 EU": "shoes",
    "US 8": "shoes",
    "35 EU": "shoes",
    "36 EU": "shoes",
    "37 EU": "shoes",
    "38 EU": "shoes",
    "45 EU": "shoes",
    "46 EU": "shoes",
    "US 7": "shoes",
    "US 9": "shoes",
    "US 10": "shoes",
    "XXS": "clothing",
    "3XL": "clothing",
    "EU 34": "clothing",
    "EU 36": "clothing",
    "EU 38": "clothing",
    "EU 40": "clothing",
    "EU 42": "clothing",
    "W30/L32": "clothing",
    "W32/L34": "clothing",
    "90 cm": "accessories",
    "100 cm": "accessories",
    "7.0 (S)": "accessories",
    "8.0 (L)": "accessories",
    "56 cm": "accessories",
    "60 cm": "accessories",
    "180x30 cm": "accessories",
    "One Size": "accessories",
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
        self.products_set: dict[str, Product] = {}
        self.products_variants_set: dict[str, ProductVariant] = {}

    def _write(self, message: str):
        if self.stdout and self.style:
            self.stdout.write(self.style.SUCCESS(message))

    def run_all(self):

        process = psutil.Process(os.getpid())
        start_time = time.perf_counter()
        psutil.cpu_percent(interval=None)

        self._write("🚀 Starting data loading...")

        self._upload_brands()
        self._upload_categories()
        self._upload_colors()
        self._upload_sizes()
        self._upload_products()
        self._upload_product_variants()

        elapsed_time = time.perf_counter() - start_time
        cpu_usage = psutil.cpu_percent(interval=None)

        ram_mb = process.memory_info().rss / (1024 * 1024)

        self._write("\n" + "=" * 40)
        self._write(f"⏱️ Час виконання: {elapsed_time:.2f} сек")
        self._write(f"💻 Завантаження CPU (Python): {cpu_usage:.1f}%")
        self._write(f"🧠 Використання RAM (Python): {ram_mb:.2f} MB")
        self._write("=" * 40)

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

    def _upload_colors(self):
        Color.objects.bulk_create(
            (
                Color(
                    name=color_name,
                    hex_code=hex_code,
                    is_active=True,
                )
                for color_name, hex_code in COLORS.items()
            ),
            ignore_conflicts=True,
        )

        self.colors_set = {color.name: color for color in Color.objects.all()}

        self._write(f"Colors {len(self.colors_set)} loaded successfully")

    def _upload_sizes(self):
        Size.objects.bulk_create(
            (
                Size(
                    name=name,
                    size_type=size_type,
                )
                for name, size_type in SIZES.items()
            ),
            ignore_conflicts=True,
        )

        self.sizes_set = {size.name: size for size in Size.objects.all()}

        self._write(f"Sizes {len(self.sizes_set)} loaded successfully")

    def _upload_products(self):
        Product.objects.bulk_create(
            (
                Product(
                    name=f"Product {elem}",
                    slug=generate_unique_slug(Product, f"Product {elem}"),
                    description=FAKE.text(),
                    brand=random.choice(list(self.brands_set.values())),
                    subcategory=random.choice(list(self.subcategories_set.values())),
                    is_active=True,
                    is_hidden=False,
                )
                for item, elem in enumerate(range(1, 300))
            ),
            ignore_conflicts=True,
        )

        self.products_set = {
            product.name: product
            for product in Product.objects.select_related("brand", "subcategory").all()
        }
        self._write(f"Products {len(self.products_set)} loaded successfully")

    def _upload_product_variants(self):
        ProductVariant.objects.bulk_create(
            (
                ProductVariant(
                    product=random.choice(list(self.products_set.values())),
                    size=random.choice(list(self.sizes_set.values())),
                    color=random.choice(list(self.colors_set.values())),
                    sku=f"SKU-Product-{elem}-{random.randint(10000, 99999)}",
                    stock=random.randint(0, 300),
                    price=round(random.uniform(10.0, 500.0), 2),
                    gender=random.choice([item for item in Gender.values]),
                    is_active=True,
                )
                for item, elem in enumerate(range(1, 2000))
            ),
            ignore_conflicts=True,
        )

        self.products_variants_set = {
            product_variant.sku: product_variant
            for product_variant in ProductVariant.objects.select_related(
                "product", "size", "color"
            ).all()
        }
        self._write(
            f"Product Variants {len(self.products_variants_set)} loaded successfully"
        )
