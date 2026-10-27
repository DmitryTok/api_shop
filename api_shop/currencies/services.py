import re

from django.conf import settings
from django.db.models import DecimalField, OuterRef, Subquery
from rest_framework import serializers

from .models import Currency

CURRENCY_CODE_RE = re.compile(r"^[A-Z]{3}$")


def resolve_currency_code(raw: str | None) -> str:
    """Normalize a requested currency code, falling back to the store default."""
    code = (raw or "").strip().upper() or settings.DEFAULT_CURRENCY_CODE

    if not CURRENCY_CODE_RE.match(code):
        raise serializers.ValidationError(
            {"currency_code": "Must be a 3-letter currency code, e.g. UAH."}
        )

    return code


def price_subquery(currency_code: str, variant_ref: str) -> Subquery:
    """Price of a product variant in ``currency_code`` as an SQL subquery.

    ``variant_ref`` is the outer column that holds the variant id: "pk" when
    annotating ProductVariant, "product_variant_id" when annotating CartItem.
    A variant without a price in that currency gets NULL. If it has several
    rows for the same currency, the newest one wins.
    """
    return Subquery(
        Currency.objects.filter(
            product_variant=OuterRef(variant_ref),
            currency_code__iexact=currency_code,
        )
        .order_by("-created_at", "-id")
        .values("amount")[:1],
        output_field=DecimalField(max_digits=10, decimal_places=2),
    )
