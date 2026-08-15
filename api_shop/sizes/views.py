from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Size
from .serializers import SizeSerializer


class SizeListAPIView(ListAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class SizeRetrieveAPIView(RetrieveAPIView):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
