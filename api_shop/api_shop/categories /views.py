from rest_framework.viewsets import ModelViewSet
from .models import Category
from .serializers import CategorySerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(is_active=is_active_bool)

        order_by = self.request.query_params.get("order_by")
        allowed_fields = ["name", "-name", "id", "-id"]
        if order_by in allowed_fields:
            queryset = queryset.order_by(order_by)

        return queryset

    def perform_create(self, serializer):
        serializer.save()


     