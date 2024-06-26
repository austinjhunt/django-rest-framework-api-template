from django.conf import settings
from rest_framework import serializers
from api.models import User, Profile
import logging

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)


class SignUpSerializer(serializers.Serializer):

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        logger.info({"action": "UserSignUpSerializer.validate", "data": data})

        # if user already exists return error
        if User.objects.filter(username=data.get("email")).exists():
            logger.error(
                {
                    "action": "UserSignUpSerializer.validate",
                    "error": "A user with this username already exists.",
                }
            )
            raise serializers.ValidationError("A user with this username already exists.")
        return data

    def create(self, validated_data):
        logger.info({"action": "UserSignUpSerializer.create", "validated_data": validated_data})
        # create a new user
        user = User.objects.create_user(
            username=validated_data.get("email"),
            email=validated_data.get("email"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            password=validated_data.get("password"),
        )
        user.is_active = False
        user.save()
        profile = Profile.objects.create(user=user)
        profile.save()
        return user

