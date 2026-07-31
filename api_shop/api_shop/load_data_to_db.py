from django.core.exceptions import ValidationError

from brands.serializers import BrandSerializer
from categories.serializers import SubcategorySerializer, CategorySerializer
from colors.serializers import ColorSerializer
from currencies.serializers import CurrencySerializer
from discounts.serializers import DiscountSerializer
from product_images.serializers import ProductImageSerializer
from product_variants.serializers import ProductVariantSerializer
from products.serializers import ProductSerializer
from profiles.serializers import ProfileSerializer
from sizes.serializers import SizeSerializer
from users.serializers import UserSerializer

serializers = [BrandSerializer, CategorySerializer, SubcategorySerializer, ColorSerializer, CurrencySerializer, DiscountSerializer,
               ProductImageSerializer, ProductVariantSerializer, ProductSerializer, ProfileSerializer, SizeSerializer, UserSerializer]


def check_serializer_type(data):
    if not data:
        return None

    for serializer_class in serializers:
        serializer = serializer_class(data=data)

        if serializer.is_valid():
            return serializer_class

    return None


def read_data_from_file(data):
    if not data or not isinstance(data, list):
        raise ValidationError("There is no data in file")

    dict_instance = data[0]
    fields = dict_instance.get("fields", dict_instance)
    serializer = check_serializer_type(fields)

    if not serializer:
        raise ValidationError("Invalid data or matching serializer not found")

    load_data_to_db(serializer_class=serializer, data=data)


def load_data_to_db(serializer_class, data):
    for instance in data:
        fields = instance.get("fields", instance)
        serializer = serializer_class(data=fields)
        if serializer.is_valid():
            serializer.save()
        else:
            raise ValidationError(f"{instance} is invalid format object. "
                                  f"Please make sure all objects in file are "
                                  f"valid and have same format for a specific database.")
    return None
