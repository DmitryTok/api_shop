import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from favorites.models import Favorite
from products.models import Product
from product_variants.models import Gender, ProductVariant
from sizes.models import Kind, Size
from users.models import CustomUser


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="user@example.com",
        password="testpassword123",
        is_active=True,
    )


@pytest.fixture
def second_user():
    return CustomUser.objects.create_user(
        email="second@example.com",
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
def test_favorite_list_requires_authentication(api_client):
    url = reverse("favorite-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_favorite(api_client, user, variant):
    api_client.force_authenticate(user=user)

    url = reverse("favorite-list")
    response = api_client.post(
        url,
        {"product_variant": variant.pk},
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["user"] == user.pk
    assert response.data["product_variant"] == variant.pk
    

@pytest.mark.django_db
def test_user_sees_only_own_favorites(
    api_client,
    user,
    second_user,
    variant,
):
    Favorite.objects.create(
        user=user,
        product_variant=variant,
    )
    Favorite.objects.create(
        user=second_user,
        product_variant=variant,
    )

    api_client.force_authenticate(user=user)

    url = reverse("favorite-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["user"] == user.pk


@pytest.mark.django_db
def test_delete_own_favorite(api_client, user, variant):
    favorite = Favorite.objects.create(
        user=user,
        product_variant=variant,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "favorite-detail",
        kwargs={"pk": favorite.pk},
    )
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Favorite.objects.filter(pk=favorite.pk).exists()


@pytest.mark.django_db
def test_user_cannot_delete_another_users_favorite(
    api_client,
    user,
    second_user,
    variant,
):
    favorite = Favorite.objects.create(
        user=second_user,
        product_variant=variant,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "favorite-detail",
        kwargs={"pk": favorite.pk},
    )
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Favorite.objects.filter(pk=favorite.pk).exists()


@pytest.mark.django_db
def test_retrieve_own_favorite(api_client, user, variant):
    favorite = Favorite.objects.create(
        user=user,
        product_variant=variant,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "favorite-detail",
        kwargs={"pk": favorite.pk},
    )
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == favorite.pk
    assert response.data["user"] == user.pk
    assert response.data["product_variant"] == variant.pk
