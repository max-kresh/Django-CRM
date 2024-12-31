"""
Tests for common apis
"""

from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

from common.models import AppSettings
from common.serializer import AppSettingsSerializer

APP_SETTINGS_URL = reverse("common_urls:api_common:app-settings")


def create_setting(**setting_params):
    return AppSettings.objects.create(**setting_params)


class PublicCommonApiTests(TestCase):
    """Tests for public common apis"""

    def setUp(self):
        self.client = APIClient()

    def test_get_settings_success(self):
        """Test if get settings api return setting"""

        setting_params = {
            "name" : "allow_google_login",
            "value": "True",
            "type" : "bool"
        }
        
        setting = create_setting(**setting_params)
        
        res = self.client.get(APP_SETTINGS_URL, {"name":setting_params["name"]})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        fields = res.json()[0]
        for field in fields:
            self.assertEqual(fields[field], getattr(setting, field))

    def test_non_admin_update_setting_fail(self):
        """Test user that are not admin cannot update setting"""

        setting_update = {
            "name": "allow_google_login",
            "value": "False",
        }

        setting_original = {
            "name": "allow_google_login",
            "value": "True",
            "type": "bool"
        }
        setting = create_setting(**setting_original)

        # user = create_user(**{"email": "test_user@example.com", "password": "password123"})
        # user.is_staff = True
        
        res = self.client.put(APP_SETTINGS_URL, setting_update)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        setting.refresh_from_db()
        self.assertEqual(setting.value, setting_original["value"])


class PrivateCommonApiTests(TestCase):
    """Tests for private common apis"""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(**{"email":"admin@example.com", "password":"password123"})
        # self.user.is_staff = True
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_admin_update_setting_success(self):
        """Test admins can update setting"""

        setting_update = {
            "name": "allow_google_login",
            "value": "False",
        }

        setting_original = {
            "name": "allow_google_login",
            "value": "True",
            "type": "bool"
        }
        setting = create_setting(**setting_original)
        print("\n\n************setting: ", setting)
        
        res = self.client.put(APP_SETTINGS_URL, setting_update)
        print("\n\n************res: ",res.json())

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        setting.refresh_from_db()
        self.assertEqual(setting.value, setting_update["value"])



