from rest_framework.viewsets import ModelViewSet
from .serializers import BrandSerializer
from .models import Brand


class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
