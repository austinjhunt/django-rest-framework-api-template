from api.tests.base import (
    BaseTestCase,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
    TEST_USER_BIO,
    TEST_USER_PREFERRED_NAME,
)

from rest_framework import status
from django.urls import reverse


class TestGetProfile(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_basic_test_user()

    def test_get_profile_fail_unauthenticated(self):
        response = self.client.get(reverse("api:get-profile"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("detail"), "Authentication credentials were not provided."
        )

    def test_get_profile_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("api:get-profile"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("first_name"), self.user.first_name)
        self.assertEqual(response.data.get("last_name"), self.user.last_name)
        self.assertEqual(response.data.get("email"), self.user.email)
        self.assertEqual(response.data.get("bio"), self.user.profile.bio)
        self.assertEqual(response.data.get("preferred_name"), self.user.profile.preferred_name)
        self.assertEqual(response.data.get("card_last4"), self.user.profile.card_last4)
        self.assertEqual(response.data.get("card_type"), self.user.profile.card_type)
        self.assertEqual(response.data.get("plan_type"), self.user.profile.plan_type)


class TestEditProfile(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.create_basic_test_user()

    def test_edit_profile_fail_unauthenticated(self):
        response = self.client.patch(reverse("api:edit-profile"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data.get("detail"), "Authentication credentials were not provided."
        )

    def test_edit_profile_fail_no_data(self):
        # at least one field should be provided
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse("api:edit-profile"), {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("message"), "No data provided for update")

    def test_edit_profile_success(self):
        self.client.force_authenticate(user=self.user)
        self.assertEqual(self.user.first_name, TEST_USER_FIRST_NAME)
        self.assertEqual(self.user.last_name, TEST_USER_LAST_NAME)
        self.assertEqual(self.user.profile.bio, TEST_USER_BIO)
        self.assertEqual(self.user.profile.preferred_name, TEST_USER_PREFERRED_NAME)

        response = self.client.patch(
            reverse("api:edit-profile"),
            {
                "first_name": "New First Name",
                "last_name": "New Last Name",
                "bio": "New Bio",
                "preferred_name": "New Preferred Name",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "New First Name")
        self.assertEqual(self.user.last_name, "New Last Name")
        self.assertEqual(self.user.profile.bio, "New Bio")
        self.assertEqual(self.user.profile.preferred_name, "New Preferred Name")
        self.assertEqual(self.user.profile.card_last4, self.user.profile.card_last4)
        self.assertEqual(self.user.profile.card_type, self.user.profile.card_type)
        self.assertEqual(self.user.profile.plan_type, self.user.profile.plan_type)
