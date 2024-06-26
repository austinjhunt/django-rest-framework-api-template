# Path: project/api/tests/unit/test_create_user.py

from api.tests.base import (
    BaseTestCase,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
)


class TestCreateUser(BaseTestCase):
    def test_create_user(self):
        user = self.create_basic_test_user()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, TEST_USER_USERNAME)
        self.assertEqual(user.email, TEST_USER_EMAIL)
        self.assertEqual(user.first_name, TEST_USER_FIRST_NAME)
        self.assertEqual(user.last_name, TEST_USER_LAST_NAME)
        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(TEST_USER_PASSWORD))
        self.assertIsNotNone(user.profile)
