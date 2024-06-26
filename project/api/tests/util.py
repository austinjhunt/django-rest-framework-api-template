# Path: project/api/tests/util.py

# Utility functions used for testing


####################################
########### USER CREATION ##########
####################################
from api.util import create_user

# Define constants that can be used for expected values in tests
TEST_USER_USERNAME = "testuser@gmail.com"
TEST_USER_EMAIL = TEST_USER_USERNAME
TEST_USER_PASSWORD = "testpassword"
TEST_USER_FIRST_NAME = "Test"
TEST_USER_LAST_NAME = "User"

def create_basic_test_user():
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
    )
    return user