# Path: project/api/tests/views/test_password.py
from api.tests.base import BaseTestCase, TEST_USER_EMAIL, TEST_USER_PASSWORD
from django.urls import reverse
from rest_framework import status
from django.conf import settings



class TestSendPasswordResetEmail(BaseTestCase):
    """
    Test for the SendPasswordResetEmail view
    """

    def test_send_password_reset_email_success(self):
        """
        Test sending a password reset email
        """
        user = self.create_basic_test_user()
        user.is_active = True
        user.save()
        response = self.client.post(
            reverse("api:send-password-reset-email"),
            {"email": TEST_USER_EMAIL, "host": settings.FRONTEND_URL},
        )
        # Email will not send for test user but that is OK. we just need the make sure the token is present.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get("token"))
        self.assertEqual(response.data.get("message"), "Could not send password reset email")

    def test_send_password_reset_email_fail_dne_user(self):
        """
        Test sending a password reset email fails
        """
        response = self.client.post(
            reverse("api:send-password-reset-email"),
            {"email": TEST_USER_EMAIL, "host": settings.FRONTEND_URL},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "A user with this email does not exist.")
        self.assertIsNotNone(response.data.get("token"))


class TestPasswordReset(BaseTestCase):
    """
    Test for the PasswordReset view
    """

    def setUp(self):
        # go ahead and get a token to use for password reset since that is what
        # we are testing here, not the token generation itself.
        super().setUp()
        self.user = self.create_basic_test_user()
        self.user.is_active = True
        self.user.save()

        response = self.client.post(
            reverse("api:send-password-reset-email"),
            {"email": TEST_USER_EMAIL, "host": settings.FRONTEND_URL},
        )
        # Email will not send for test user but that is OK. we just need the make sure the token is present.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get("token"))
        self.assertEqual(response.data.get("message"), "Could not send password reset email")

        self.password_reset_token = response.data.get("token")

    def test_verify_password_reset_token_success(self):
        """
        Test verifying a password reset token
        """
        response = self.client.post(
            reverse("api:verify-password-reset-token"),
            {"token": self.password_reset_token, "user_id": self.user.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Token is valid")

    def test_set_new_password_anonymous_success(self):
        """
        Test password reset flow in entirety. Ignore email sending functionality for now.
        """
        response = self.client.patch(
            reverse("api:set-new-password-anonymous"),
            {
                "user_id": self.user.id,
                "token": self.password_reset_token,
                "password": "newpassword",
                "confirm_password": "newpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Password reset successfully")


    def test_set_new_password_anonymous_fail_invalid_token(self):
        """
        Test password reset fails with invalid token
        """
        response = self.client.patch(
            reverse("api:set-new-password-anonymous"),
            {
                "user_id": self.user.id,
                "token": "invalidtoken",
                "password": "newpassword",
                "confirm_password": "newpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("message"), "Invalid token")

    def test_set_new_password_anonymous_fail_invalid_user(self):
        """
        Test password reset fails with invalid user
        """
        response = self.client.patch(
            reverse("api:set-new-password-anonymous"),
            {
                "user_id": -20,
                "token": self.password_reset_token,
                "password": "newpassword",
                "confirm_password": "newpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "User with this id does not exist.")

    def test_set_new_password_anonymous_fail_invalid_passwords(self):
        """
        Test password reset fails with invalid passwords
        """
        response = self.client.patch(
            reverse("api:set-new-password-anonymous"),
            {
                "user_id": self.user.id,
                "token": self.password_reset_token,
                "password": "newpassword",
                "confirm_password": "mismatchedpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "New password does not match confirmation password.")


    def test_set_new_password_authenticated_success(self):
        """
        Test password reset flow in entirety. Ignore email sending functionality for now.
        """
        # log in
        response = self.client.post(
            reverse("api:login"),
            {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data.get("token")}')
        # set new password
        response = self.client.patch(
            reverse("api:set-new-password-authenticated"),
            {
                "current_password": TEST_USER_PASSWORD,
                "new_password": "testnewpassword",
                "confirm_new_password": "testnewpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Password reset successfully")

    def test_set_new_password_authenticated_fail_invalid_current_password(self):
        """
        Test password reset fails with invalid current password
        """
        # log in
        response = self.client.post(
            reverse("api:login"),
            {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data.get("token")}')
        # set new password
        response = self.client.patch(
            reverse("api:set-new-password-authenticated"),
            {
                "current_password": "invalidpassword",
                "new_password": "testnewpassword",
                "confirm_new_password": "testnewpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("message"), "Invalid current password.")

    def test_set_new_password_authenticated_fail_invalid_passwords(self):
        """
        Test password reset fails with invalid passwords
        """
        # log in
        response = self.client.post(
            reverse("api:login"),
            {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {response.data.get("token")}')

        # set new password
        response = self.client.patch(
            reverse("api:set-new-password-authenticated"),
            {
                "current_password": TEST_USER_PASSWORD,
                "new_password": "testnewpassword",
                "confirm_new_password": "mismatchedpassword",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "New password does not match confirmation password.")