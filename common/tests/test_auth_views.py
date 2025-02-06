import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from common.token_generator import account_activation_token
from django.utils import timezone


from common.tests.factories import (
    OrgFactory,
    UserFactory,
    ProfileFactory,
    AddressFactory,
)
from rest_framework_simplejwt.tokens import RefreshToken
# class UserLoginViewTests(APITestCase):
#     def setUp(self):
#         # Create Organization
#         self.org1 = OrgFactory()
#         # Create an user
#         self.regular_user_data={"email": "regular@example.com", "password": "regularpass"}
#         self.regular_user = UserFactory(email=self.regular_user_data["email"])
#         self.regular_user.set_password(self.regular_user_data["password"])
#         self.regular_user.save()
        
#         refresh = RefreshToken.for_user(self.regular_user)
#         self.regular_access_token = str(refresh.access_token)

    
    
#         self.url = reverse("common_urls:api_common:user-login")
    
#     def test_user_login(self):
#         """
#         Ensure we can login with valid credentials.
#         """
       
#         response = self.client.post(self.url, data=self.regular_user_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["username"], "regular@example.com")
#         self.assertTrue("access_token" in response.data)
    
#     def test_user_login_with_invalid_pass(self):
#         """
#         Ensure we can't login with invalid credentials.
#         """
#         # wrong pass
#         invalid_data={"email": "regular@example.com", "password": "regularwrongpass"}
#         response = self.client.post(self.url, data=invalid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        
    
#     def test_user_login_with_invalid_email(self):
#         """
#         Ensure we can't login with invalid email.
#         """
#         # wrong email
#         invalid_data={"email": "wrongregular@example.com,", "password": "regularpass"}
#         response = self.client.post(self.url, data=invalid_data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class CreatePasswordViewTests(APITestCase):
    def setUp(self):
        self.regular_user=UserFactory(email="regular@email.com")
        self.regular_user.set_password("regularpass")
        self.regular_user.save()
        self.uid = (urlsafe_base64_encode(force_bytes(self.regular_user.pk)),)
        self.token = account_activation_token.make_token(self.regular_user)
        time_delta_two_hours = datetime.datetime.strftime(
            timezone.now() + datetime.timedelta(hours=2), "%Y-%m-%d-%H-%M-%S"
        )
        self.activation_key = self.token + time_delta_two_hours
        self.regular_user.activation_key = self.activation_key
        self.regular_user.save()
        self.url = reverse("common_urls:api_common:create-password")
    
    def test_create_password(self):
        """
        Ensure we can create password with valid token and uid.
        """
        data={"uid": self.uid[0], "user_token": self.token, "user_token_delta": self.activation_key, "password": "newpassword"}
        response = self.client.post(self.url, data=data, format="json")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Login with new credentials
        login_url = reverse("common_urls:api_common:user-login")
        login_data={"email": self.regular_user.email, "password": "newpassword"}
        login_response = self.client.post(login_url, data=login_data, format="json")
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue("access_token" in login_response.data)
    
    def test_create_password_with_invalid_token(self):
        """
        Ensure we can't create password with invalid token.
        """
        data={"uid": self.uid[0], "user_token": "invalidtoken", "user_token_delta": self.activation_key, "password": "newpassword"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_password_with_invalid_uid(self):
        """
        Ensure we can't create password with invalid uid.
        """
        data={"uid": "invaliduid", "user_token": self.token, "user_token_delta": self.activation_key, "password": "newpassword"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_password_with_invalid_token_delta(self):
        """
        Ensure we can't create password with invalid token delta.
        """
        data={"uid": self.uid[0], "user_token": self.token, "user_token_delta": "invalidtoken", "password": "newpassword"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



