# views.py
import stripe
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.util import send_payment_complete_confirmation_email

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntent(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=settings.ENROLL_IN_COURSE_SECTION_COST_CENTS,  # $10.00, this is in cents
                currency="usd",
                payment_method_types=["card"],
            )
            return Response(
                {"clientSecret": payment_intent["client_secret"]}, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)


class SendPaymentCompleteConfirmation(APIView):
    def get(self, request, section_id):
        payment_amount = settings.PREMIUM_CHARGE_AMOUNT
        try:
            email_sent = send_payment_complete_confirmation_email(
                recipient=request.user.email,
                first_name=request.user.first_name,
                subject="Novabrains Enrollment Payment Confirmation",
                course_title=course_title,
                section_number=section_number,
                payment_amount=payment_amount,
            )
            if email_sent:
                return Response({"message": "Email sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Email failed to send"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

