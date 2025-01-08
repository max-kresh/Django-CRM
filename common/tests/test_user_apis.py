"""
Tests for user apis
"""

from django.test import TestCase
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from common.models import Org, Profile
from common.serializer import UserCreateSwaggerSerializer

USER_URL = reverse("common_urls:api_common:users-list")
USER_DETAIL_URL = reverse("common_urls:api_common:users-list")

def create_user(role):
    if role == "ADMIN":
        user = get_user_model().objects.create_superuser(
            **{"email":"test@example.com", "password":"password123"}
        )
    else:
        user = get_user_model().objects.create_user(
            **{"email":"test@example.com", "password":"password123"}
        )
    return user

payload = {
    "email": "test1@example.com",
    "role": "USER",
    "address_line": "Test Address", 
    "phone": "+31684250000",
    "alternate_phone": "+31684250001",
    "street": "New Street",
    "city": "New City",
    "state": "New state",
    "pincode": "123456",
    "country": "New Country",
    "profile_pic": None,
    "has_sales_access": False,
    "has_marketing_access": False,
    "is_organization_admin": False,
}

header = {
    "org": "Test_Org"
}


class PublicUserApiTests(TestCase):
    """Tests for public user apis on user-list url"""

    def setUp(self):
        self.user = create_user("USER")
        
        self.org = Org.objects.create(name="Test_Org", api_key="test_key")
        self.org.save() 
        self.profile = Profile.objects.create(org=self.org, user=self.user, role="USER")
        self.profile.save()
        self.user.save()

        self.client = APIClient()
        self.client.force_authenticate(self.user)       


    def test_create_user_fails_for_non_admin_users(self):
        """Test if non admin users cannot create user"""
        

        res = self.client.post(USER_URL, payload, format="json", org=header["org"])

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

class PrivateUserApiTests(TestCase):
    """Tests for private user apis on user-list url"""

    def setUp(self):
        self.user = create_user("ADMIN")

        self.client = APIClient()
        self.client.force_authenticate(self.user)       

    @patch("common.middleware.get_company.GetProfileAndOrg.__call__")
    def test_create_user_success(self, mock_middleware):
        """Test if admin users can create user. Due to 
        the setting in middleware this test is not working"""

        mock_middleware.return_value = None

        res = self.client.post(USER_URL, payload, format="json", org=header["org"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        created_user = get_user_model().objects.get(email=payload["email"])
        role = created_user.profile.first().role
        self.assertEqual(role, payload["role"])