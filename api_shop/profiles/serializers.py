from profiles.models import Profile
from rest_framework.serializers import ModelSerializer
from users.serializers import UserSerializer


class ProfileSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ("id", "user")
