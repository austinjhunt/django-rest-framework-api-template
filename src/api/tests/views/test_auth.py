# Path: project/api/tests/views/test_auth.py

from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from api.tests.base import (
    BaseTestCase,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
)


class TestLogin(BaseTestCase):
    """
    Test for the Login view
    """

    def setUp(self):
        super().setUp()
        # user not active yet.
        self.user = self.create_basic_test_user()

    def test_login_fail_not_active(self):
        """
        Test login fails when user is not active
        """
        response = self.client.post(
            reverse("api:login"), {"username": TEST_USER_USERNAME, "password": TEST_USER_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("error"), "Invalid credentials or account not activated yet"
        )

    def test_login_fail_incorrect_credentials(self):
        """
        Test login fails when incorrect credentials are provided
        """
        self.user.is_active = True
        self.user.save()
        response = self.client.post(
            reverse("api:login"), {"username": TEST_USER_USERNAME, "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("error"), "Invalid credentials or account not activated yet"
        )

    def test_login_success(self):
        """
        Test login success
        """
        self.user.is_active = True
        self.user.save()
        response = self.client.post(
            reverse("api:login"), {"username": TEST_USER_USERNAME, "password": TEST_USER_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("token"))
        self.assertEqual(response.data.get("username"), TEST_USER_USERNAME)
        self.assertEqual(response.data.get("email"), TEST_USER_EMAIL)
        self.assertEqual(response.data.get("preferred_name"), self.user.profile.preferred_name)

class TestLogout(BaseTestCase):
    """
    Test for the Logout view
    """

    def test_logout_success(self):
        """
        Test logout
        """
        # First need to log in. Which means we need the user and they need to be active.
        user = self.create_basic_test_user()
        user.is_active = True
        user.save()
        response = self.client.post(
            reverse("api:login"), {"username": TEST_USER_USERNAME, "password": TEST_USER_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data.get("token"))

        # update client authorization header with token
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data.get('token')}")

        # verify that the token is valid / user is logged in with auth-check
        response = self.client.get(reverse("api:auth-check"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), TEST_USER_USERNAME)

        # use the token to logout
        response = self.client.post(reverse("api:logout"))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # check if token is deleted
        response = self.client.get(reverse("api:auth-check"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_fail_no_token(self):
        """
        Test logout fails when no token is provided
        """
        response = self.client.post(reverse("api:logout"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)



class TestSignUp(BaseTestCase):
    """
    Test for the SignUp view
    """

    def test_signup_success(self):
        """
        Test signup success
        """
        response = self.client.post(
            reverse("api:signup"),
            {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "first_name": TEST_USER_FIRST_NAME,
                "last_name": TEST_USER_LAST_NAME,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get("user_id"))
        self.assertIsNotNone(response.data.get("token"))  # token for activation
        self.assertEqual(
            response.data.get("message"),
            f"Your account was created. Please check your email ({TEST_USER_EMAIL}) for a link to activate your account.",
        )

    def test_signup_fail_duplicate_username(self):
        """
        Test signup fails when duplicate username is provided
        """
        user = self.create_basic_test_user()
        response = self.client.post(
            reverse("api:signup"),
            {
                "first_name": TEST_USER_FIRST_NAME,
                "last_name": TEST_USER_LAST_NAME,
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "A user with this username already exists.")


class TestActivateAccount(BaseTestCase):
    """
    Test for the ActivateAccount view
    """

    def setUp(self):
        super().setUp()

    def test_activate_account_fail_invalid_uidb64(self):
        """
        Test activation fails when invalid uidb64 is provided
        """
        self.user = self.create_basic_test_user()
        response = self.client.get(
            reverse("api:activate-account", kwargs={"uidb64": "invalid", "token": "validtoken"})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Activation link is invalid!")

    def test_activate_account_fail_invalid_token(self):
        """
        Test activation fails when invalid token is provided
        """
        self.user = self.create_basic_test_user()
        response = self.client.get(
            reverse("api:activate-account", kwargs={"uidb64": self.user.pk, "token": "invalidtoken"})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("error"), "Activation link is invalid!")

    def test_activate_account_success_already_active(self):
        """
        Test activation succeeds when user is already active
        """
        self.user = self.create_basic_test_user()
        self.user.is_active = True
        self.user.save()
        response = self.client.get(
            reverse("api:activate-account", kwargs={"uidb64": self.user.pk, "token": "validtoken"})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "Account already activated!")

    def test_activate_account_success(self):
        """
        Test activation success
        """
        signup_response = self.client.post(
            reverse("api:signup"),
            {
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "first_name": TEST_USER_FIRST_NAME,
                "last_name": TEST_USER_LAST_NAME,
            },
        )
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)
        self.user = User.objects.get(id=signup_response.data.get("user_id"))
        # user still not active
        self.assertFalse(self.user.is_active)

        # get the activation token from signup response
        activation_token = signup_response.data.get("token")

        response = self.client.get(
            reverse("api:activate-account", kwargs={"uidb64": self.user.pk, "token": activation_token})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "User activated successfully")
        self.user.refresh_from_db()
        # user should be active now
        self.assertTrue(self.user.is_active)
