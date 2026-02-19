from rest_framework.viewsets import ModelViewSet
from profiles.serializers import ProfileSerializer
from profiles.models import Profile


class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileSerializer
    lookup_url_kwarg = "profile_id"
    http_method_names = ["get", "put", "patch"]
