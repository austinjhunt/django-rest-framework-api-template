# Path: project/api/tests/base.py

# Base class for all tests - contains utility methods and constants


####################################
########### USER CREATION ##########
####################################
from api.util import create_user
from rest_framework.test import APITestCase

# Define constants that can be used for expected values in tests
TEST_USER_USERNAME = "testuser@gmail.com"
TEST_USER_EMAIL = TEST_USER_USERNAME
TEST_USER_PASSWORD = "testpassword"
TEST_USER_FIRST_NAME = "Test"
TEST_USER_PREFERRED_NAME = "Test Preferred Name"
TEST_USER_LAST_NAME = "User"
TEST_USER_BIO = "Test bio content for the test user profile"

class BaseTestCase(APITestCase):

    def create_basic_test_user(self):
        """
        Create a basic test user with default values
        """
        user = create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME,
            is_active=False,
            bio=TEST_USER_BIO,
            preferred_name=TEST_USER_PREFERRED_NAME,
        )
        return user