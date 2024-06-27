from api.serializers.base import BaseSerializer
from rest_framework import serializers
from django.contrib.auth.models import User

class SendPasswordResetEmailRequestSerializer(BaseSerializer):
    email = serializers.EmailField()
    host = serializers.CharField()

    def validate_email(self, email):
        if not User.objects.filter(username=email).exists():
            raise serializers.ValidationError("A user with this email does not exist.")
        return email

class SendPasswordResetEmailResponseSerializer(BaseSerializer):
    message = serializers.CharField()
    token = serializers.CharField()


class VerifyPasswordResetTokenRequestSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()

    def validate_user_id(self, user_id):
        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError(f"User with this id does not exist.")
        return user_id


class SetNewPasswordAnonymousRequestSerializer(BaseSerializer):
    user_id = serializers.IntegerField()
    token = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError("New password does not match confirmation password.")
        return data

    def validate_user_id(self, user_id):
        if not User.objects.filter(id=user_id).exists():
            raise serializers.ValidationError(f"User with this id does not exist.")
        return user_id

class SetNewPasswordAuthenticatedRequestSerializer(BaseSerializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

    def validate(self, data):
        if data.get("new_password") != data.get("confirm_new_password"):
            raise serializers.ValidationError("New password does not match confirmation password.")
        return data

class SetNewPasswordResponseSerializer(BaseSerializer):
    message = serializers.CharField()