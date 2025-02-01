"""
Tests for user apis
"""
from random import randint
from django.test import TestCase
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from common.utils import Constants

from common.tests.mock_utils import mock_crm_middleware, create_test_user

USER_URL = reverse("common_urls:api_common:users-list")

payload = {
    "email": "test1@example.com",
    "role": Constants.USER,
    "phone": "+31684250" + str(randint(0, 9)) + str(randint(0, 9)) + str(randint(0, 9)),    
}


class PrivateUserApiTests(TestCase):
    """Tests for private user apis on user-list url"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = create_test_user(role=Constants.ADMIN)      
        self.non_admin_user = create_test_user(role=Constants.USER)

    @mock_crm_middleware("non_admin_user")
    def test_create_user_fails_for_non_admin_users(self):
        """Test if non admin users cannot create user"""

        res = self.client.post(USER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


    @mock_crm_middleware("admin_user")
    def test_create_user_success(self):
        """Test if admin users can create a user."""

        res = self.client.post(USER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        created_user = get_user_model().objects.get(email=payload["email"])
        role = created_user.profile.first().role
        self.assertEqual(role, payload["role"])
