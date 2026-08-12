import pytest

from profiles.models import ClothingSize, Gender, Profile
from profiles.serializers import ProfileSerializer
from users.models import CustomUser


@pytest.mark.django_db
def test_profile_serializer():
    user = CustomUser.objects.create_user(
        email="user@example.com",
        password="testpassword123",
        is_active=True,
    )

    profile = user.profile
    profile.first_name = "Anna"
    profile.last_name = "Smith"
    profile.gender = Gender.FEMALE
    profile.clothing_size = ClothingSize.M
    profile.shoe_size = 38
    profile.save()

    serializer = ProfileSerializer(profile)

    assert serializer.data["first_name"] == "Anna"
    assert serializer.data["last_name"] == "Smith"
    assert serializer.data["shoe_size"] == 38


@pytest.mark.django_db
def test_profile_serializer_displays_gender_and_clothing_size():
    user = CustomUser.objects.create_user(
        email="user2@example.com",
        password="testpassword123",
        is_active=True,
    )

    profile = user.profile
    profile.gender = Gender.FEMALE
    profile.clothing_size = ClothingSize.M
    profile.save()

    serializer = ProfileSerializer(profile)

    assert serializer.data["gender"] == "FEMALE"
    assert serializer.data["clothing_size"] == "M"


@pytest.mark.django_db
def test_profile_serializer_user_is_read_only():
    user = CustomUser.objects.create_user(
        email="user3@example.com",
        password="testpassword123",
        is_active=True,
    )

    profile = user.profile
    profile.first_name = "Anna"
    profile.save()

    serializer = ProfileSerializer(
        profile,
        data={
            "first_name": "Maria",
            "user": 99999,
        },
        partial=True,
    )

    assert serializer.is_valid()
    serializer.save()

    profile.refresh_from_db()

    assert profile.first_name == "Maria"
    assert profile.user == user
