# Path: project/api/tests/views/test_auth.py

from api.tests.util import (
    create_basic_test_user,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
)


class TestLogin(APITestCase):
    """
    Test for the Login view
    """

    def setUp(self):
        super().setUp()
        # user not active yet.
        self.user = create_basic_test_user()

    def test_login_fail_not_active(self):
        """
        Test login fails when user is not active
        """
        response = self.client.post(
            reverse("api:login"), {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("detail"), "User account is disabled.")


