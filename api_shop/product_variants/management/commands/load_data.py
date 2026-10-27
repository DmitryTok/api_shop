from addons.cli_command_data_loader import DataLoader
from django.core.management.base import BaseCommand

from product_variants.models import ProductVariant


class Command(BaseCommand):
    help = "Load initial categories and subcategories"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-run even if demo product variants already exist (creates more duplicates).",
        )

    def handle(self, *args, **options):
        if not options["force"] and ProductVariant.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Product variants already exist — skipping to avoid duplicating "
                    "demo data. Pass --force to reseed anyway."
                )
            )
            return

        data_loader = DataLoader(self.stdout, self.style)
        data_loader.run_all()

        self.stdout.write(self.style.SUCCESS("Command completed"))
