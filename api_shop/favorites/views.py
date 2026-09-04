from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteUserSerializer


class FavoriteViewSet(ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteUserListAPIView(ListAPIView):
    serializer_class = FavoriteUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            Favorite.objects.filter(user=self.request.user)
            .select_related(
                "product_variant__size",
                "product_variant__color",
            )
            .prefetch_related("product_variant__images")
        )
