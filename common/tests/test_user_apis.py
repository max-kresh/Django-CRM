"""
Tests for user apis
"""
from random import randint
from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models import Q

from common.utils import Constants
from common.tests.mock_utils import create_test_user
from common.tests.mock_utils import middleware_mocker

USER_URL = reverse("common_urls:api_common:users-list")

TEST_ORG_NAME = "Test_Org"

payload = {
    "email": "test1@example.com",
    "role": Constants.USER,
    "phone": "+31684250" + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)),    
}


class PrivateUserApiTests(TestCase):
    """Tests for private user apis on user-list url"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_test_user(org_name=TEST_ORG_NAME, role=Constants.ADMIN)      
        self.non_admin_user = create_test_user(org_name=TEST_ORG_NAME, role=Constants.USER)
    
    # def middleware_mocker(self, request):
    #     request.profile = self.admin_user.profile.filter(
    #         Q(user=self.admin_user), Q(org__name=TEST_ORG_NAME)).first()
    #     return None

    @patch("common.middleware.get_company.GetProfileAndOrg.process_request")
    def test_create_user_fails_for_non_admin_users(self, middleware_mock):
        """Test if non admin users cannot create user"""

        self.client.force_authenticate(self.non_admin_user)
        middleware_mock.side_effect = lambda request: middleware_mocker(request, self.non_admin_user, TEST_ORG_NAME)

        res = self.client.post(USER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


    @patch("common.middleware.get_company.GetProfileAndOrg.process_request")
    def test_create_user_success(self, middleware_mock):
        """Test if admin users can create a user."""

        self.client.force_authenticate(self.admin_user)
        
        middleware_mock.side_effect = lambda request: middleware_mocker(request, self.admin_user, TEST_ORG_NAME)

        res = self.client.post(USER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        created_user = get_user_model().objects.get(email=payload["email"])
        role = created_user.profile.first().role
        self.assertEqual(role, payload["role"])
