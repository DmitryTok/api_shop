import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.db import transaction
from dotenv import load_dotenv
from faker import Faker
from profiles.models import Profile

from users.models import Term, UserTermsAcceptance

load_dotenv()

FAKE = Faker()

User = get_user_model()

SEED_LOCK_KEY = "seed:load_users:done"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-run even if this command already ran before (creates more fake users).",
        )

    def handle(self, *args, **options):
        if not options["force"] and cache.get(SEED_LOCK_KEY):
            self.stdout.write(
                self.style.WARNING(
                    "load_users already ran on this environment — skipping to avoid "
                    "duplicating fake users. Pass --force to reseed anyway."
                )
            )
            return

        terms = Term.objects.filter(is_active=True).latest("created_at")

        if not terms:
            self.stdout.write(self.style.ERROR("No Active Terms found"))
            return

        users = [
            User(
                email=FAKE.unique.email(),
                password=make_password(
                    os.getenv("CUSTOM_PASSWORD", default="Password123!")
                ),
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
            for _ in range(11)
        ]

        try:
            with transaction.atomic():
                created_users = User.objects.bulk_create(users)

                created_profiles = Profile.objects.bulk_create(
                    Profile(id=user.id, user=user) for user in created_users
                )

                created_terms = UserTermsAcceptance.objects.bulk_create(
                    UserTermsAcceptance(user=user, terms=terms)
                    for user in created_users
                )

            cache.set(SEED_LOCK_KEY, True, timeout=None)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {len(created_users)} users"
                    f"{len(created_profiles)} profiles"
                    f"{len(created_terms)} terms_acceptances"
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error occurred while creating data: {e}")
            )
