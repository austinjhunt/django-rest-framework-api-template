from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from django.conf import settings

from api.serializers import (
    EditProfileRequestSerializer,
    MessageResponseSerializer,
    ProfileSerializer,
)

import logging

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)


class EditProfile(views.APIView):
    """
    Allow user to edit profile
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=EditProfileRequestSerializer,
        responses={200: ProfileSerializer, 400: MessageResponseSerializer},
    )
    def patch(self, request):
        try:
            if request.user.is_anonymous:
                return Response(
                    {"message": "Unauthorized"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            serializer = EditProfileRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"message": serializer.get_simple_error()},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = request.user
            data = serializer.validated_data

            if data.get("first_name"):
                user.first_name = data.get("first_name")
            if data.get("last_name"):
                user.last_name = data.get("last_name")
            if data.get("bio"):
                user.profile.bio = data.get("bio")
            if data.get("preferred_name"):
                user.profile.preferred_name = data.get("preferred_name")
            user.profile.save()
            user.save()
            return Response(
                user.profile.format_json(),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error({
                "message": f"Could not update profile",
                "error": str(e)
            })
            return Response(
                {"message": f"Could not update profile"},
                status=status.HTTP_400_BAD_REQUEST,
            )

class GetProfile(views.APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        responses={200: ProfileSerializer, 400: MessageResponseSerializer},
    )
    def get(self, request):
        try:
            return Response(
                request.user.profile.format_json(),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error({
                "message": f"Could not get profile",
                "error": str(e)
            })
            return Response(
                {"message": f"Could not get profile"},
                status=status.HTTP_400_BAD_REQUEST,
            )