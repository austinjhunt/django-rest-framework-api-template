# Path: project/api/tests/util.py

# Utility functions used for testing


####################################
########### USER CREATION ##########
####################################
from api.util import create_user

# Define constants that can be used for expected values in tests
TEST_USER_USERNAME = "testuser"
TEST_USER_EMAIL = "testuser@gmail.com"
TEST_USER_PASSWORD = "testpassword"
TEST_USER_FIRST_NAME = "Test"
TEST_USER_LAST_NAME = "User"

def create_basic_test_user():
    """
    Create a basic test user with default values
    """
    user = create_user(
        username="testuser",
        email="email",
        password="testpassword",
        first_name="Test",
        last_name="User",
        is_active=False,
    )
    return user