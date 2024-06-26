import logging

import requests
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.recaptcha import (
    VerifyRecaptchaRequestSerializer,
    VerifyRecaptchaResponseSerializer,
)

logger = logging.getLogger("api")


class VerifyRecaptcha(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=VerifyRecaptchaRequestSerializer, responses=VerifyRecaptchaResponseSerializer
    )
    def post(self, request):
        try:
            token = request.data.get("token")
            url = f"https://www.google.com/recaptcha/api/siteverify?secret={settings.RECAPTCHA_SECRET_KEY}&response={token}"
            response = requests.post(url)
            result = response.json()
            logger.info(
                {
                    "action": "VerifyRecaptcha.post",
                    "result": result,
                }
            )
            if result["success"]:
                return Response({"success": True})
            return Response({"success": False})
        except Exception as e:
            logger.error(
                {
                    "action": "VerifyRecaptcha.post",
                    "error": str(e),
                }
            )
            return Response({"success": False})
