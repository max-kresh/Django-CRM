"""
Tests for common.app_settings apis

"""

from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from common.models import AppSettings
from common.tests.mock_utils import middleware_mocker
from common.utils import Constants

from common.tests.mock_utils import create_test_user

APP_SETTINGS_URL = reverse("common_urls:api_common:app-settings")

TEST_ORG_NAME = "Test_Org"

setting_update = {
    "name": AppSettings.SETTING_CHOICES[0][0], # "allow_google_login",
    "value": "False",
}

setting_original = {
    "type": "bool",
    **setting_update
}


def create_setting(**setting_params):
    return AppSettings.objects.create(**setting_params)


class PublicAppSettingsApiTests(TestCase):
    """Tests for public common apis"""

    def setUp(self):
        # Currently app_settings are pre-populated into db when the 
        # server initializes (so does the test db). Since setting_name  
        # is constrained with an option we cannot create test data 
        #  without cleaning the test db first. 
        AppSettings.objects.all().delete()

        AppSettings.objects.create(**setting_original)
        self.client = APIClient()

    def test_get_settings_success(self):
        """Test if get settings api return setting"""
        
        res = self.client.get(APP_SETTINGS_URL, {"name":setting_original["name"]})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        setting = AppSettings.objects.get(name=setting_original["name"])
        fields = res.json()[0]
        for field in fields:
            self.assertEqual(fields[field], getattr(setting, field))

class PrivateAppSettingsApiTests(TestCase):
    """Tests for private common apis"""

    def setUp(self):
        # Currently app_settings are pre-populated into db when the 
        # server initializes (so does the test db). Since setting_name  
        # is constrained with an option we cannot create test data 
        #  without cleaning the test db first. 
        AppSettings.objects.all().delete()

        self.admin_user = create_test_user(role=Constants.ADMIN, org_name=TEST_ORG_NAME)
        self.admin_user.save()

        self.non_admin_user = create_test_user(role=Constants.USER, org_name=TEST_ORG_NAME)
        self.non_admin_user.save()
        
        self.client = APIClient()
    
    @patch("common.middleware.get_company.GetProfileAndOrg.process_request")
    def test_non_admin_update_setting_fail(self, middleware_mock):
        """Test non-admin user cannot update setting"""

        setting = create_setting(**setting_original)

        middleware_mock.side_effect = lambda request: middleware_mocker(request, self.non_admin_user, TEST_ORG_NAME)

        self.client.force_authenticate(self.non_admin_user)
        res = self.client.put(APP_SETTINGS_URL, setting_update)

        # self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        setting.refresh_from_db()
        self.assertEqual(setting.value, setting_original["value"])

    @patch("common.middleware.get_company.GetProfileAndOrg.process_request")
    def test_admin_update_setting_success(self, middleware_mock):
        """Test admins can update setting"""

        setting = create_setting(**setting_original)
        
        self.client.force_authenticate(self.admin_user)

        middleware_mock.side_effect = lambda request: middleware_mocker(request, self.admin_user, TEST_ORG_NAME)
        
        res = self.client.put(APP_SETTINGS_URL, setting_update)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        setting.refresh_from_db()
        self.assertEqual(setting.value, setting_update["value"])



