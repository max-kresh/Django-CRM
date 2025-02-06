from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch


from common.tests.factories import (
    OrgFactory,
    UserFactory,
    ProfileFactory,
    AddressFactory,
)
from rest_framework_simplejwt.tokens import RefreshToken
class CreateOrgProfileViewTests(APITestCase):
    def setUp(self):
        # Create Organization
        self.org1 = OrgFactory()
        # Create an user
        self.regular_user = UserFactory(email="regular")
        self.regular_user.set_password("regularpass")
        self.regular_user.save()
        
        refresh = RefreshToken.for_user(self.regular_user)
        self.regular_access_token = str(refresh.access_token)

    
    
        self.url = reverse("common_urls:api_common:org-profile")
    # Create Organization and organization's admin profile
    def test_create_org_with_profile(self):
        """
        Ensure we can create a new org and the organization's admin profile object which is assigned to authenticated request user.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_access_token)
        data={"name": "TestOrg"}
        response = self.client.post(self.url, data=data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["org"]["name"], "TestOrg")
    
    def test_create_org_as_unauthenticated_user(self):
        """
        Ensure we can't create a new org as unauthenticated user.
        """
        data={"name": "TestOrg"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_org_with_invalid_input(self):
        """
        Ensure we can't create a new org with invalid input.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_access_token)
        data={"name": "Test Org"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # Get request user's organizations 
    def test_get_user_orgs(self):
        """
        Ensure we can get request user's organizations.
        """
        user_organization_count=5
        for i in range(user_organization_count):
            org=OrgFactory()
            ProfileFactory(user=self.regular_user, org=org, role="ADMIN" if i%2==0 else "USER",is_active=True)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.regular_access_token)
        response = self.client.get(self.url)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["profile_org_list"]), user_organization_count)



