from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from django.conf import settings

import logging

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)

@permission_classes([AllowAny])
class SendPasswordResetEmail(views.APIView):
    def post(self, request):
        try:
            email = request.data.get("email")
            host = request.data.get("host")
            user = User.objects.get(email=email)
            first_name = user.first_name
            token = PasswordResetTokenGenerator().make_token(user)
            if send_password_reset_email(
                recipient=email,
                first_name=first_name,
                subject=f"{settings.APP_NAME} Password Reset",
                reset_link=f"{host}/reset-password/{user.id}/{token}",
            ):
                return Response({"message": "Email sent", token: token})
            raise Exception("Could not send email")
        except Exception as e:
            logger.error(e)
            return Response(
                {"error": f"Could not send password reset email"},
                status=400,
            )


@permission_classes([AllowAny])
class VerifyPasswordResetToken(views.APIView):
    def post(self, request):
        try:
            user_id = request.data.get("userId")
            token = request.data.get("token")
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"error": f"Invalid token"},
                    status=400,
                )
            return Response({"message": "Token is valid"})
        except Exception as e:
            logger.error(e)
            return Response(
                {"error": f"Could not verify token"},
                status=400,
            )

@permission_classes([AllowAny])
class SetNewPassword(views.APIView):
    """The following view is used to set a new password for a user.
    The user does not need to be logged in for this.
    We use the user id and token (hidden form inputs included in the request)
    to verify the token is valid before reseting the password.
    """

    def patch(self, request):
        try:
            if request.user.is_anonymous:
                # for the "Forgot Password" flow, the user is not logged in
                # so we need to get the user from the request data
                # and verify the token is valid
                user_id = request.data.get("userId")
                token = request.data.get("token")
                password = request.data.get("password")
                user = User.objects.get(id=user_id)
                if not PasswordResetTokenGenerator().check_token(user, token):
                    return Response(
                        {"error": f"Invalid token"},
                        status=401,
                    )
                user.set_password(password)
                user.save()
                return Response({"message": "Password reset successfully"}, status=200)
            else:
                # For the "Change Password" flow, the user is logged in and
                # must provide their current password to set a new password
                current_password = request.data.get("current_password")
                new_password = request.data.get("new_password")
                user = request.user
                if not user.check_password(current_password):
                    return Response(
                        {"error": f"Invalid password"},
                        status=401,
                    )
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password reset successfully"}, status=200)
        except Exception as e:
            logger.error(e)
            return Response(
                {"error": f"Could not reset password"},
                status=400,
            )

