import pytest

from brands.serializers import BrandSerializer


@pytest.mark.django_db
def test_create_brand_without_slug():
    data = {
        "name": "Nike",
    }

    serializer = BrandSerializer(data=data)

    assert serializer.is_valid()
    brand = serializer.save()

    assert brand.slug == "nike"