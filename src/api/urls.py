from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from api.views import *

app_name = "api"

urlpatterns = [
    ##############################
    ##### AUTHENTICATION #########
    ##############################
    # include default login and logout views for use with the browsable API.
    # this is optional but useful if your API requires authentication and you
    # want to use the browsable API.
    path("auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("signup/", auth.SignUp.as_view(), name="signup"),
    path("login/", auth.Login.as_view(), name="login"),
    path("logout/", auth.Logout.as_view(), name="logout"),
    path("auth_check/", auth.AuthCheck.as_view(), name="auth-check"),
     # front end app should always have a proxy to this url
    # (frontend.ai/activate_account/<uidb64>/<token>/ -> backend.ai/activate_account/<uidb64>/<token>)
    path(
        "activate_account/<uidb64>/<token>/",
        auth.ActivateAccount.as_view(),
        name="activate-account",
    ),

    ##################################
    ##### PASSWORD MGMT ##############
    ##################################
    path(
        "send_password_reset_email/",
        password.SendPasswordResetEmail.as_view(),
        name="send-password-reset-email",
    ),
    path(
        "verify_password_reset_token/",
        password.VerifyPasswordResetToken.as_view(),
        name="verify-password-reset-token",
    ),
    path(
        "set_new_password_anonymous/",
        password.SetNewPasswordAnonymous.as_view(),
        name="set-new-password-anonymous",
    ),
    path(
        "set_new_password_authenticated/",
        password.SetNewPasswordAuthenticated.as_view(),
        name="set-new-password-authenticated",
    ),


    ##############################
    ##### PROFILE ##############
    ##############################
    path(
        "edit_profile/",
        profile.EditProfile.as_view(),
        name="edit-profile",
    ),
    path(
        "get_profile/",
        profile.GetProfile.as_view(),
        name="get-profile",
    ),

    ##############################
    ##### SWAGGER ##############
    ##############################
    path("schema/", swagger.SpectacularSwagger.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),

    ##############################
    ##### STRIPE PAYMENT #########
    ##############################
    path("create_payment_intent/", payment.CreatePaymentIntent.as_view(), name="create-payment-intent"),
    path(
        "send_payment_complete_confirmation/<uuid:section_id>/",
        payment.SendPaymentCompleteConfirmation.as_view(),
        name="send-payment-complete-confirmation",
    ),


    ##############################
    ##### RECAPTCHA ##############
    path("verify_recaptcha/", recaptcha.VerifyRecaptcha.as_view(), name="verify-recaptcha"),

]
