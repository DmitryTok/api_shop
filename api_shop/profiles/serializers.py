from profiles.models import ClothingSize, Gender, Profile
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from users.serializers import UserSerializer
from validators.validators_profiles import profile_phone_validator, profile_birthday_validator


class ProfileSerializer(ModelSerializer):
    gender = serializers.ChoiceField(
        choices=Gender.choices(), source='get_gender_display'
    )
    clothing_size = serializers.ChoiceField(
        choices=ClothingSize.choices(), source='get_clothing_size_display'
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ("id", "user")
        validators = [profile_phone_validator, profile_birthday_validator]
