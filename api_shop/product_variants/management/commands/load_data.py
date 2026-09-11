from addons.cli_command_data_loader import DataLoader
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load initial categories and subcategories"

    def handle(self, *args, **options):

        data_loader = DataLoader(self.stdout, self.style)
        data_loader.run_all()

        self.stdout.write(self.style.SUCCESS("Command completed"))
