from rest_framework import serializers


class VerifyRecaptchaRequestSerializer(serializers.Serializer):
    token = serializers.CharField()


class VerifyRecaptchaResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
