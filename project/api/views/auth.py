from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import IntegrityError


from api.serializers import SignUpSerializer, LoginSerializer
from api.tokens import AccountActivationTokenGenerator
from api.util import send_activate_account_email

import logging

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)

@permission_classes([AllowAny])
class ActivateAccount(views.APIView):
    def get(self, request, uidb64, token):
        try:
            user = User.objects.get(pk=uidb64)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            logger.error(e)
            user = None

        if user and user.is_active:
            return Response(
                {"message": "Account already activated!"},
                status=200,
            )

        if user is not None and AccountActivationTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()
            logger.info(
                {
                    "action": "ActivateAccount.get",
                    "user": user.username,
                    "message": "User activated successfully",
                }
            )
            return Response(
                {"message": "User activated successfully"},
                status=200,
            )
        else:
            logger.error(f"User: {user}; activation failed!")
            return Response(
                {"error": "Activation link is invalid!"},
                status=400,
            )

class Logout(APIView):
    def post(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AuthCheck(APIView):
    def get(self, request):
        if request.user.is_anonymous:
            return Response({}, status=401)
        else:
            return Response(
                {
                    "username": request.user.username,
                    "email": request.user.email,
                    "preferred_name": request.user.profile.preferred_name,
                },
                status=200,
            )


class Login(APIView):
    permission_classes = [AllowAny]
    @extend_schema(
        request=LoginSerializer,
    )

    def post(self, request, format=None):

        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.get_simple_error(), status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            result = {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "preferred_name": user.profile.preferred_name,
            }

            return Response(result)
        else:
            return Response(
                {"error": "Invalid credentials or account not activated yet"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token = AccountActivationTokenGenerator().make_token(user)
                logger.info(
                    {
                        "action": "SignUp.post",
                        "message": "Account created successfully, must activate account with email link",
                    }
                )
                send_activate_account_email(
                    recipient=user.email,
                    first_name=user.first_name,
                    subject=f"Activate {settings.APP_NAME} Account",
                    activate_link=(f"{settings.FRONTEND_URL}/activate_account/{user.id}/{token}"),
                )


                return Response(
                    {
                        "message": f"Your account was created. Please check your email ({user.email}) for a link to activate your account.",
                        "user_id": user.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(
                    {
                        "action": "SignUp.post",
                        "error": str(e),
                    }
                )
                return Response(
                    {
                        "error": "An error occurred while creating your account. Please try again later or contact support for assistance."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            logger.error(
                {
                    "action": "SignUp.post",
                    "error": serializer.errors,
                }
            )
            # flatte
            return Response(serializer.get_simple_error(), status=status.HTTP_400_BAD_REQUEST)
