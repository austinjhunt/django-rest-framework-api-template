# Path: project/api/tests/views/test_auth.py
from rest_framework import status
from django.urls import reverse
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
        self.assertEqual(response.data.get("error"), "Invalid credentials or account not activated yet")

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
        self.assertEqual(response.data.get("error"), "Invalid credentials or account not activated yet")

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
                "username": TEST_USER_USERNAME,
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "first_name": TEST_USER_FIRST_NAME,
                "last_name": TEST_USER_LAST_NAME,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data.get("user_id"))
        self.assertEqual(response.data.get("message"), f"Your account was created. Please check your email ({TEST_USER_EMAIL}) for a link to activate your account.")

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
            })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('error'), "A user with this username already exists.")




