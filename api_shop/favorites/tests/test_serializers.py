import pytest
from rest_framework.test import APIRequestFactory

from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from favorites.models import Favorite
from favorites.serializers import FavoriteSerializer
from products.models import Product
from product_variants.models import Gender, ProductVariant
from sizes.models import Kind, Size
from users.models import CustomUser


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="user@example.com",
        password="testpassword123",
        is_active=True,
    )


@pytest.fixture
def variant():
    brand = Brand.objects.create(
        name="Nike",
        slug="nike",
    )
    category = Category.objects.create(
        name="Women",
        slug="women",
    )
    subcategory = Subcategory.objects.create(
        category=category,
        name="T-Shirts",
        slug="t-shirts",
    )
    product = Product.objects.create(
        name="Nike T-Shirt",
        slug="nike-t-shirt",
        brand=brand,
        subcategory=subcategory,
    )
    size = Size.objects.create(
        name="S",
        size_type=Kind.CLOTHING,
        sort_order=1,
    )
    color = Color.objects.create(
        name="White",
        hex_code="#FFFFFF",
    )

    return ProductVariant.objects.create(
        product=product,
        size=size,
        color=color,
        sku="NIKE-WHITE-S",
        stock=10,
        gender=Gender.UNISEX,
    )


@pytest.mark.django_db
def test_duplicate_favorite_serializer_validation(user, variant):
    Favorite.objects.create(
        user=user,
        product_variant=variant,
    )

    request = APIRequestFactory().post("/")
    request.user = user

    serializer = FavoriteSerializer(
        data={"product_variant": variant.pk},
        context={"request": request},
    )

    assert not serializer.is_valid()
    assert "product_variant" in serializer.errors
    assert (
        str(serializer.errors["product_variant"][0])
        == "This product variant is already in favorites."
    )
    