from django.conf import settings
from rest_framework import serializers
from api.serializers.base import BaseSerializer
from api.models import User, Profile
from api.util import get_simple_serializer_error
import logging

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)


class SignUpRequestSerializer(BaseSerializer):

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        logger.info({"action": "SignUpSerializer.validate", "data": data})
        if User.objects.filter(username=data.get("email")).exists():
            logger.error(
                {
                    "action": "SignUpSerializer.validate",
                    "error": "A user with this username already exists.",
                }
            )
            raise serializers.ValidationError("A user with this username already exists.")
        return data

    def create(self, validated_data):
        logger.info({"action": "SignUpSerializer.create", "validated_data": validated_data})
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

class SignUpResponseSerializer(BaseSerializer):
    message = serializers.CharField()
    user_id = serializers.UUIDField()
    token = serializers.CharField()

class LoginRequestSerializer(BaseSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        logger.info({"action": "LoginSerializer.validate", "data": data})
        user = User.objects.filter(username=data.get("username")).first()
        if user is None:
            logger.error(
                {
                    "action": "LoginSerializer.validate",
                    "error": "A user with this username does not exist.",
                }
            )
            raise serializers.ValidationError("A user with this username does not exist.")
        return data

class LoginResponseSerializer(BaseSerializer):
    token = serializers.CharField()
    username = serializers.CharField()
    preferred_name = serializers.CharField()