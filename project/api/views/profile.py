from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from django.conf import settings

import logging
logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)

class EditProfile(views.APIView):
    """
    Allow user to edit profile
    """

    def patch(self, request):
        try:
            user = request.user
            if user.is_anonymous:
                return Response(
                    {},
                    status=401,
                )

            # verify that keys are present in request.data
            if not request.data.get("basic_info"):
                return Response(
                    {"error": f"Invalid request data"},
                    status=400,
                )

            response = {}
            if request.data.get("basic_info"):
                basic_info = request.data.get("basic_info")
                user.first_name = basic_info.get("first_name")
                user.last_name = basic_info.get("last_name")
                user.email = basic_info.get("email")
                user.profile.bio = basic_info.get("bio")
                user.profile.save()
                user.save()
                response["basic_info_updated"] = {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "bio": user.profile.bio,
                }

            return Response(response, status=200)
        except Exception as e:
            logger.error(e)
            return Response(
                {"error": f"Could not update profile"},
                status=400,
            )


class GetProfile(views.APIView):
    def get(self, request):
        try:
            user = request.user
            if user.is_anonymous:
                return Response(
                    {},
                    status=401,
                )
            profile = user.profile
            return Response(
                {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "profile": profile.format_json()
                },
                status=200,
            )
        except Exception as e:
            logger.error(e)
            return Response(
                {"error": f"Could not get profile"},
                status=400,
            )
