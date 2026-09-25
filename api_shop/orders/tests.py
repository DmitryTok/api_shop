from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from brands.models import Brand
from categories.models import Category, Subcategory
from colors.models import Color
from products.models import Product
from product_variants.models import ProductVariant
from shopping_cart.models import CartItem, ShoppingCart
from sizes.models import Size
from orders.models import Order


User = get_user_model()


class OrderCreateAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        brand = Brand.objects.create(
            name="Test Brand",
            slug="test-brand",
        )
        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
        )
        subcategory = Subcategory.objects.create(
            category=category,
            name="Test Subcategory",
            slug="test-subcategory",
        )

        product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            brand=brand,
            subcategory=subcategory,
        )

        size = Size.objects.create(
            name="M",
            size_type="clothing",
        )
        color = Color.objects.create(
            name="Black",
            hex_code="#000000",
        )

        self.variant = ProductVariant.objects.create(
            product=product,
            size=size,
            color=color,
            sku="TEST-SKU-001",
            stock=10,
            price="100.00",
        )

        self.cart = ShoppingCart.objects.create(user=self.user)

        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product_variant=self.variant,
            quantity=2,
        )
        self.order_data = {
            "first_name": "Test",
            "last_name": "User",
            "phone": "+380991234567",
            "delivery_method": "nova_post",
            "city": "Kharkiv",
            "branch_number": "1",
            "payment_method": "card",
            "cart_item_ids": [self.cart_item.id],
        }

    def test_create_order_with_available_item(self):
        response = self.client.post(
            "/api/orders/checkout/",
            self.order_data,
            format="json",
        )
       

        self.assertEqual(response.status_code, 201)
        self.variant.refresh_from_db()

        self.assertEqual(self.variant.stock, 8)

    def test_order_not_created_when_item_is_unavailable(self):
        self.variant.stock = 1
        self.variant.save(update_fields=["stock"])

        response = self.client.post(
            "/api/orders/checkout/",
            self.order_data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(Order.objects.exists())

    def test_checkout_skips_unavailable_item(self):
        unavailable_variant = ProductVariant.objects.create(
            product=self.variant.product,
            size=self.variant.size,
            color=self.variant.color,
            sku="TEST-SKU-002",
            stock=1,
            price="50.00",
        )
        unavailable_cart_item = CartItem.objects.create(
            cart=self.cart,
            product_variant=unavailable_variant,
            quantity=2,
        )
        self.order_data["cart_item_ids"] = [
            self.cart_item.id,
            unavailable_cart_item.id,
        ]
        response = self.client.post(
            "/api/orders/checkout/",
            self.order_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.variant.refresh_from_db()
        unavailable_variant.refresh_from_db()

        self.assertEqual(self.variant.stock, 8)
        self.assertEqual(unavailable_variant.stock, 1) 

    def test_checkout_rejects_invalid_cart_item(self):
        self.order_data["cart_item_ids"] = [
            self.cart_item.id,
            999999,
        ]

        response = self.client.post(
            "/api/orders/checkout/",
            self.order_data,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
        response.data["detail"],
        "Invalid cart items.",
        )
        self.assertFalse(Order.objects.exists())
