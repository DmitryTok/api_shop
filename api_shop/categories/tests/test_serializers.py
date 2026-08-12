import pytest

from categories.serializers import (
    CategorySerializer,
    SubcategorySerializer,
)


@pytest.mark.django_db
def test_create_category_without_slug():
    serializer = CategorySerializer(
        data={"name": "Women"}
    )

    assert serializer.is_valid()
    category = serializer.save()

    assert category.slug == "women"


@pytest.mark.django_db
def test_category_name_too_short():
    serializer = CategorySerializer(
        data={"name": "W"}
    )

    assert not serializer.is_valid()
    assert "name" in serializer.errors


@pytest.mark.django_db
def test_create_subcategory_without_slug():
    category_serializer = CategorySerializer(
        data={"name": "Women"}
    )
    assert category_serializer.is_valid()
    category = category_serializer.save()

    serializer = SubcategorySerializer(
        data={
            "name": "Dresses",
            "category": category.pk,
        }
    )

    assert serializer.is_valid()
    subcategory = serializer.save()

    assert subcategory.slug == "dresses"


@pytest.mark.django_db
def test_subcategory_name_too_short():
    serializer = SubcategorySerializer(
        data={"name": "D"}
    )

    assert not serializer.is_valid()
    assert "name" in serializer.errors
