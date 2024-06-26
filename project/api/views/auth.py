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
from django.contrib.auth import authenticate
from django.db import IntegrityError


from api.serializers import SignUpSerializer
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
                    "action": "ActivateAccountView.get",
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

        instructor = Instructor.objects.filter(user=request.user).first()
        student = Student.objects.filter(user=request.user).first()

        if instructor:
            return Response({"account_type": "instructor"}, status=200)

        elif student:
            return Response({"account_type": "student"}, status=200)

        elif request.user.is_superuser or request.user.is_staff:
            return Response({"account_type": "admin"}, status=200)

        else:
            return Response({}, status=401)


class Login(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            # if instructor, check if account is verified
            if user.profile.is_instructor and not user.instructor.verified:
                # return error message
                logger.error(
                    {
                        "action": "LoginView.post",
                        "error": "Instructor account has not been verified yet.",
                    }
                )
                return Response(
                    {
                        "detail": "Instructor account has not been verified yet. We will send you an email to confirm once your account has been reviewed."
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            token, _ = Token.objects.get_or_create(user=user)
            result = {
                "token": token.key,
                "username": user.username,
                "email": user.email,
            }

            # Let's determine if the user is a student or an instructor (or both)
            instructor = Instructor.objects.filter(user=user).first()
            if instructor:
                result.update({"instructor_id": instructor.id})

            student = Student.objects.filter(user=user).first()
            if student:
                result.update({"student_id": student.id})

            return Response(result)
        else:
            return Response(
                {"detail": "Invalid credentials (or account not activated yet)"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class SignUp(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token = AccountActivationTokenGenerator().make_token(user)
                logger.info(
                    {
                        "action": "UserSignUpAPIView.post",
                        "message": "Account created successfully, must activate account with email link",
                    }
                )
                send_activate_account_email(
                    recipient=user.email,
                    first_name=user.first_name,
                    subject=f"Activate {settings.APP_NAME} Account",
                    activate_link=(f"{settings.FRONTEND_URL}/activate_account/{user.id}/{token}"),
                )

                # send admins an email to notify them of the new instructor request
                # with a link to verify them
                send_instructor_signup_request_notification_to_admins(requesting_user=user)

                if role == "instructor":
                    message = f"Your instructor account has been created. You will not be able to log into your account until the NovaBrains team manually reviews and verifies your instructor status, but go ahead and check your email ({user.email}) for a link to activate your account."
                elif role == "student":
                    message = f"Your account was created. Please check your email ({user.email}) for a link to activate your account."

                return Response(
                    {
                        "message": message,
                        "user_id": user.id,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                logger.error(
                    {
                        "action": "UserSignUpAPIView.post",
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
                    "action": "UserSignUpAPIView.post",
                    "error": serializer.errors,
                }
            )
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
