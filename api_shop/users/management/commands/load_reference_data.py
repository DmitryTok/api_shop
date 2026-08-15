import typing as t

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Loads reference/demo data required for the shop: brands, categories, terms, colors, sizes"

    def handle(self, *args: t.Any, **options: t.Any) -> None:
        self.stdout.write("--> Loading brands...")
        call_command("load_brands")

        self.stdout.write("--> Loading categories...")
        call_command("load_category")

        self.stdout.write("--> Loading terms...")
        call_command("load_terms")

        self.stdout.write("--> Loading colors and sizes...")
        call_command("loaddata", "colors.json", "sizes.json")

        self.stdout.write(self.style.SUCCESS("Reference data loaded successfully"))
