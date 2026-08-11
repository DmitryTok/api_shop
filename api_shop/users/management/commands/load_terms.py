import textwrap
import typing as t

from django.core.management.base import BaseCommand

from users.models import Term


class Command(BaseCommand):
    help = "Automatically creates terms if they do not exist"

    def handle(self, *args: t.Any, **options: t.Any) -> None:
        self.stdout.write("Start loading Terms...")

        obj, created = Term.objects.get_or_create(
            version="1.0",
            text=textwrap.dedent("""
            Користувач підтверджує достовірність наданих даних.
            Користувач несе відповідальність за безпеку свого акаунта та пароля.
            Магазин залишає за собою право змінювати асортимент, ціни та умови продажу без попереднього повідомлення.
            Всі замовлення обробляються відповідно до наявності товару.
            Магазин може скасувати замовлення у випадку технічної помилки, шахрайства або неможливості виконання замовлення.
            Повернення та обмін товарів здійснюються відповідно до політики повернення.
            Персональні дані користувача обробляються відповідно до Privacy Policy.
            Створюючи акаунт, користувач підтверджує згоду з умовами використання сервісу.
            """).strip(),
            is_active=True,
        )

        if created:
            self.stdout.write(self.style.SUCCESS("Terms loaded successfully"))

        else:
            self.stdout.write(self.style.SUCCESS("Terms already exist"))
