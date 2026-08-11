from rest_framework import serializers

from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    def validate_product_variant(self, product_variant):
        user = self.context["request"].user

        if Favorite.objects.filter(
            user=user,
            product_variant=product_variant,
        ).exists():
            raise serializers.ValidationError(
                "This product variant is already in favorites."
            )

        return product_variant

    class Meta:
        model = Favorite
        fields = (
            "id",
            "user",
            "product_variant",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
        )
