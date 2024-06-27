from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from django.conf import settings

from api.util import send_password_reset_email
from api.permissions import IsAnonymous
from api.serializers import (
    MessageResponseSerializer,
    SendPasswordResetEmailRequestSerializer,
    SendPasswordResetEmailResponseSerializer,
    VerifyPasswordResetTokenRequestSerializer,
    SetNewPasswordAnonymousRequestSerializer,
    SetNewPasswordAuthenticatedRequestSerializer,
)

import logging

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)


@permission_classes([AllowAny])
class SendPasswordResetEmail(views.APIView):
    @extend_schema(
        request=SendPasswordResetEmailRequestSerializer,
        responses={
            200: SendPasswordResetEmailResponseSerializer,
            400: SendPasswordResetEmailResponseSerializer,
        },
    )
    def post(self, request):
        serializer = SendPasswordResetEmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            host = serializer.validated_data.get("host")
            user = User.objects.get(email=email)
            first_name = user.first_name
            token = PasswordResetTokenGenerator().make_token(user)
            try:
                if send_password_reset_email(
                    recipient=email,
                    first_name=first_name,
                    subject=f"{settings.APP_NAME} Password Reset",
                    reset_link=f"{host}/reset-password/{user.id}/{token}",
                ):
                    return Response(
                        {"message": "Email sent", "token": token}, status=status.HTTP_200_OK
                    )
                raise Exception("Could not send email")
            except Exception as e:
                logger.error(
                    {
                        "action": "SendPasswordResetEmail.post",
                        "error": str(e),
                    }
                )
                return Response(
                    {"message": f"Could not send password reset email", "token": token},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            serializer_error = serializer.get_simple_error()
            logger.error({"action": "SendPasswordResetEmail.post", "error": serializer_error})
            # return the error message and token (empty) for standard response schema
            return Response(
                {"message": serializer_error, "token": ""}, status=status.HTTP_400_BAD_REQUEST
            )


@permission_classes([AllowAny])
class VerifyPasswordResetToken(views.APIView):
    @extend_schema(
        request=VerifyPasswordResetTokenRequestSerializer,
        responses={200: MessageResponseSerializer, 400: MessageResponseSerializer},
    )
    def post(self, request):
        serializer = VerifyPasswordResetTokenRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user_id = request.data.get("user_id")
                token = request.data.get("token")
                user = User.objects.get(id=user_id)
                if not PasswordResetTokenGenerator().check_token(user, token):
                    return Response(
                        {"message": f"Invalid token"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(
                    {
                        "action": "VerifyPasswordResetToken.post",
                        "error": str(e),
                    }
                )
                return Response(
                    {"message": f"Could not verify token"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"message": serializer.get_simple_error()}, status=status.HTTP_400_BAD_REQUEST
            )


class SetNewPasswordAnonymous(views.APIView):
    """The following view is used to set a new password for a user.
    The user does not need to be logged in for this.
    We use the user id and token (hidden form inputs included in the request)
    to verify the token is valid before reseting the password.
    """

    permission_classes = [IsAnonymous]

    @extend_schema(
        request=SetNewPasswordAnonymousRequestSerializer,
        responses={
            200: MessageResponseSerializer,
            400: MessageResponseSerializer,
        },
    )
    def patch(self, request):
        serializer = SetNewPasswordAnonymousRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": serializer.get_simple_error()}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # for the "Forgot Password" flow, the user is not logged in
            # so we need to get the user from the request data
            # and verify the token is valid
            user_id = serializer.validated_data.get("user_id")
            token = serializer.validated_data.get("token")
            password = serializer.validated_data.get("password")
            confirm_password = serializer.validated_data.get("confirm_password")
            user = User.objects.get(id=user_id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"message": f"Invalid token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user.set_password(password)
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                {
                    "action": "SetNewPassword.patch",
                    "error": str(e),
                }
            )
            return Response(
                {"message": f"Could not reset password"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetNewPasswordAuthenticated(views.APIView):
    """The following view is used to set a new password for a user.
    The user does not need to be logged in for this.
    We use the user id and token (hidden form inputs included in the request)
    to verify the token is valid before reseting the password.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SetNewPasswordAuthenticatedRequestSerializer,
        responses={
            200: MessageResponseSerializer,
            400: MessageResponseSerializer,
        },
    )
    def patch(self, request):
        serializer = SetNewPasswordAuthenticatedRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": serializer.get_simple_error()}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # For the "Change Password" flow, the user is logged in and
            # must provide their current password to set a new password
            current_password = serializer.validated_data.get("current_password")
            new_password = serializer.validated_data.get("new_password")
            confirm_new_password = serializer.validated_data.get("confirm_new_password")
            user = request.user
            if not user.check_password(current_password):
                return Response(
                    {"message": f"Invalid current password."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(
                {
                    "action": "SetNewPassword.patch",
                    "error": str(e),
                }
            )
            return Response(
                {"message": f"Could not reset password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
