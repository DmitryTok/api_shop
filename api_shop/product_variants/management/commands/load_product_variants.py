from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load initial categories and subcategories"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Command started"))
