from decimal import Decimal

from currencies.services import price_subquery

from .models import CartItem, ShoppingCart


def cart_items_queryset(user, currency_code: str):
    """Cart items of ``user`` with product info and a price in ``currency_code``.

    Each item gets a ``unit_price`` annotation (None when the variant has no
    price in that currency), so prices cost no extra queries.
    """
    return (
        CartItem.objects.filter(cart__user=user)
        .select_related(
            "product_variant__product",
            "product_variant__size",
            "product_variant__color",
        )
        .annotate(unit_price=price_subquery(currency_code, "product_variant_id"))
        .order_by("id")
    )


def get_cart_with_prices(user, currency_code: str) -> ShoppingCart:
    """Return the user's cart (created on first use) ready for serialization.

    Items without a price in ``currency_code`` stay in the list with a null
    price and are left out of ``total_amount``.
    """
    cart, _ = ShoppingCart.objects.get_or_create(user=user)
    items = list(cart_items_queryset(user, currency_code))

    cart.currency_code = currency_code
    cart.priced_items = items
    cart.total_amount = sum(
        (
            item.unit_price * item.quantity
            for item in items
            if item.unit_price is not None
        ),
        Decimal("0.00"),
    )

    return cart
