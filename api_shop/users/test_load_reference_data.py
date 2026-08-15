import pytest
from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from django.core.management import call_command
from sizes.models import Size

from users.models import Term


@pytest.mark.django_db
def test_load_reference_data_populates_expected_records():
    call_command("load_reference_data")

    assert Brand.objects.count() == 10
    assert Category.objects.count() == 3
    assert Subcategory.objects.count() == 30
    assert Term.objects.filter(version="1.0").exists()
    assert Color.objects.count() == 10
    assert Size.objects.count() == 38


@pytest.mark.django_db
def test_load_reference_data_is_idempotent():
    call_command("load_reference_data")
    call_command("load_reference_data")

    assert Brand.objects.count() == 10
    assert Category.objects.count() == 3
    assert Term.objects.filter(version="1.0").count() == 1
