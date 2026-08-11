from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Color
from .serializers import ColorSerializer


class ColorListAPIView(ListAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class ColorRetrieveAPIView(RetrieveAPIView):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
