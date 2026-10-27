from decimal import Decimal

from currencies.services import price_subquery, resolve_currency_code
from django.db import transaction
from product_variants.models import ProductVariant
from rest_framework import serializers
from shopping_cart.models import ShoppingCart

from .models import Order, OrderItem


def _ensure_can_be_bought(variant, quantity: int, currency_code: str) -> None:
    if variant is None:
        raise serializers.ValidationError(
            {"detail": "Some items in the cart are no longer available."}
        )

    product = variant.product

    if not (variant.is_active and product.is_active and not product.is_hidden):
        raise serializers.ValidationError(
            {"detail": f"{variant.sku} is not available."}
        )

    if variant.unit_price is None or variant.unit_price <= 0:
        raise serializers.ValidationError(
            {"detail": f"{variant.sku} has no price in {currency_code}."}
        )

    if quantity > variant.stock:
        raise serializers.ValidationError(
            {
                "detail": (
                    f"Not enough stock for {variant.sku}: "
                    f"requested {quantity}, available {variant.stock}."
                )
            }
        )


@transaction.atomic
def create_order_from_cart(user, data: dict) -> Order:
    """Turn the whole cart of ``user`` into an order.

    Everything runs in one transaction. The cart row and the variant rows are
    locked, so two checkouts can neither sell the same last unit twice nor
    build two orders from one cart. Any problem aborts the transaction and the
    cart and the stock stay untouched.
    """
    currency_code = resolve_currency_code(data.get("currency_code"))

    # Lock the cart first: a double-clicked "Place order" waits here and then
    # finds an empty cart instead of creating a duplicate order.
    cart = ShoppingCart.objects.select_for_update().filter(user=user).first()
    cart_items = list(cart.items.filter(quantity__gt=0).order_by("id")) if cart else []

    if not cart_items:
        raise serializers.ValidationError({"detail": "Cart is empty."})

    # Always lock variants in id order to avoid deadlocks between checkouts.
    variants = {
        variant.pk: variant
        for variant in ProductVariant.objects.select_for_update(of=("self",))
        .select_related("product", "size", "color")
        .annotate(unit_price=price_subquery(currency_code, "pk"))
        .filter(pk__in=[item.product_variant_id for item in cart_items])
        .order_by("pk")
    }

    order_items = []
    total_amount = Decimal("0.00")

    for cart_item in cart_items:
        variant = variants.get(cart_item.product_variant_id)
        _ensure_can_be_bought(variant, cart_item.quantity, currency_code)

        line_total = variant.unit_price * cart_item.quantity
        total_amount += line_total

        order_items.append(
            OrderItem(
                product_variant=variant,
                product_name=variant.product.name,
                sku=variant.sku,
                size=variant.size.name,
                color=variant.color.name,
                unit_price=variant.unit_price,
                quantity=cart_item.quantity,
                line_total=line_total,
            )
        )

        variant.stock -= cart_item.quantity

    order = Order.objects.create(
        user=user,
        email=user.email,
        currency_code=currency_code,
        total_amount=total_amount,
        first_name=data["first_name"],
        last_name=data["last_name"],
        phone=data["phone"],
        shipping_address=data["shipping_address"],
        comment=data.get("comment", ""),
    )

    for order_item in order_items:
        order_item.order = order

    OrderItem.objects.bulk_create(order_items)

    for variant in variants.values():
        variant.save(update_fields=["stock", "updated_at"])

    cart.items.all().delete()

    return order
