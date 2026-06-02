from rest_framework import serializers

from .models import Brand
from addons.slugify import generate_slug

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

    def create(self, validated_data):

      if not validated_data.get("slug"):
         validated_data["slug"] = generate_slug(validated_data["name"])

      return super().create(validated_data)

