from rest_framework.test import APITestCase

from brands.serializers import BrandSerializer


class BrandSerializerTestCase(APITestCase):
    def test_create_brand_without_slug(self):
        data = {
            "name": "Nike",
        }

        serializer = BrandSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        brand = serializer.save()
        self.assertEqual(brand.slug, "nike")
