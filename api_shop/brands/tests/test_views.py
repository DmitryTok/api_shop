from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from brands.models import Brand


class BrandAPITestCase(APITestCase):

    def test_brand_list(self):
        Brand.objects.create(
            name="Nike",
            slug="nike",
        )
        Brand.objects.create(
            name="Adidas",
            slug="adidas",
        )

        url = reverse("brand-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Adidas")
        self.assertEqual(response.data[1]["name"], "Nike")


    def test_brand_detail(self):
        brand = Brand.objects.create(
            name="Nike",
            slug="nike",
        )

        url = reverse("brand-detail", kwargs={"pk": brand.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Nike")
        self.assertEqual(response.data["slug"], "nike")


    def test_brand_detail_not_found(self):
        url = reverse("brand-detail", kwargs={"pk": 99999})
        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    def test_brand_list_empty(self):
        url = reverse("brand-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)