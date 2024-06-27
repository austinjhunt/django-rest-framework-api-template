# Path: api/serializers/profile.py

from rest_framework import serializers
from api.serializers.base import BaseSerializer

from api.models import Profile


class EditProfileRequestSerializer(BaseSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    bio = serializers.CharField(required=False)
    preferred_name = serializers.CharField(required=False)

    def validate(self, data):
        if not any([data.get("first_name"), data.get("last_name"), data.get("bio"), data.get("preferred_name")]):
            raise serializers.ValidationError("No data provided for update")
        return data

class ProfileSerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    bio = serializers.CharField()
    preferred_name = serializers.CharField()
    card_last4 = serializers.CharField()
    card_type = serializers.CharField()
    plan_type = serializers.CharField()

