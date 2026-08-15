from rest_framework import serializers

from .models import Discount


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = (
            "id",
            "product_variant",
            "discount_type",
            "amount",
            "start_at",
            "end_at",
            "is_active",
        )
