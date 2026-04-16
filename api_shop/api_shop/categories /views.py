from rest_framework.viewsets import ModelViewSet
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # 🔎 Фільтр по назві
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        # 🔎 Фільтр по активності
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # 🔎 Сортування
        order_by = self.request.query_params.get("order_by")
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    def perform_create(self, serializer):
        serializer.save()