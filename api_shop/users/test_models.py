import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

User = get_user_model()


@pytest.mark.django_db
def test_create_user_persists_to_database():
    user = User.objects.create_user(email="crud@example.com", password="Test1234!")

    assert User.objects.filter(pk=user.pk).exists()


@pytest.mark.django_db
def test_read_user_by_email():
    User.objects.create_user(email="readme@example.com", password="Test1234!")

    fetched = User.objects.get(email="readme@example.com")

    assert fetched.email == "readme@example.com"


@pytest.mark.django_db
def test_update_user_persists_change():
    user = User.objects.create_user(email="updateme@example.com", password="Test1234!")

    user.first_name = "Updated"
    user.save()

    fetched = User.objects.get(pk=user.pk)
    assert fetched.first_name == "Updated"


@pytest.mark.django_db
def test_delete_user_removes_from_database():
    user = User.objects.create_user(email="deleteme@example.com", password="Test1234!")
    user_id = user.pk

    user.delete()

    assert not User.objects.filter(pk=user_id).exists()


@pytest.mark.django_db
def test_email_uniqueness_enforced_at_db_level():
    User.objects.create_user(email="dupe@example.com", password="Test1234!")

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            User.objects.create_user(email="dupe@example.com", password="Test1234!")
