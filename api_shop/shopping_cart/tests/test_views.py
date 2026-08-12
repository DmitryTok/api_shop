import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from product_variants.models import Gender, ProductVariant
from products.models import Product
from shopping_cart.models import CartItem, ShoppingCart
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
def test_shopping_cart_list(api_client, user):
    api_client.force_authenticate(user=user)

    url = reverse("shopping-cart-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert ShoppingCart.objects.filter(user=user).exists()
    assert response.data["user"] == user.pk
    assert response.data["items"] == []


@pytest.mark.django_db
def test_cart_item_queryset_contains_only_current_user_items(
    api_client,
    user,
    second_user,
    variant,
):
    user_cart = ShoppingCart.objects.create(user=user)
    second_user_cart = ShoppingCart.objects.create(user=second_user)

    user_item = CartItem.objects.create(
        cart=user_cart,
        product_variant=variant,
        quantity=1,
    )

    CartItem.objects.create(
        cart=second_user_cart,
        product_variant=variant,
        quantity=2,
    )

    api_client.force_authenticate(user=user)

    url = reverse("cart-items-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == user_item.pk


@pytest.mark.django_db
def test_create_cart_item(api_client, user, variant):
    api_client.force_authenticate(user=user)

    url = reverse("cart-items-list")
    response = api_client.post(
        url,
        {
            "product_variant": variant.pk,
            "quantity": 2,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED

    cart = ShoppingCart.objects.get(user=user)
    item = CartItem.objects.get(
        cart=cart,
        product_variant=variant,
    )

    assert item.quantity == 2
    assert response.data["product_variant"] == variant.pk
    assert response.data["quantity"] == 2


@pytest.mark.django_db
def test_create_existing_cart_item_adds_quantity(
    api_client,
    user,
    variant,
):
    cart = ShoppingCart.objects.create(user=user)

    item = CartItem.objects.create(
        cart=cart,
        product_variant=variant,
        quantity=2,
    )

    api_client.force_authenticate(user=user)

    url = reverse("cart-items-list")
    response = api_client.post(
        url,
        {
            "product_variant": variant.pk,
            "quantity": 3,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    item.refresh_from_db()

    assert item.quantity == 5
    assert response.data["quantity"] == 5


@pytest.mark.django_db
def test_partial_update_cart_item(api_client, user, variant):
    cart = ShoppingCart.objects.create(user=user)

    item = CartItem.objects.create(
        cart=cart,
        product_variant=variant,
        quantity=2,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "cart-items-detail",
        kwargs={"pk": item.pk},
    )

    response = api_client.patch(
        url,
        {"quantity": 4},
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK

    item.refresh_from_db()
    assert item.quantity == 4


@pytest.mark.django_db
def test_partial_update_zero_quantity_deletes_item(
    api_client,
    user,
    variant,
):
    cart = ShoppingCart.objects.create(user=user)

    item = CartItem.objects.create(
        cart=cart,
        product_variant=variant,
        quantity=2,
    )

    api_client.force_authenticate(user=user)

    url = reverse(
        "cart-items-detail",
        kwargs={"pk": item.pk},
    )

    response = api_client.patch(
        url,
        {"quantity": 0},
        format="json",
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not CartItem.objects.filter(pk=item.pk).exists()
    