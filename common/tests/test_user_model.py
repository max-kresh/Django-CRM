from django.contrib.auth import get_user_model
from django.test import TestCase
from common.models import User, Profile
from common.utils import Constants

class ModelTest(TestCase):
    """Tests for user roles"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password")
        

    def test_set_user_role_success(self):
        print("test_set_user_role_success")
        profile = Profile.objects.create(user=self.user)
        profile.role = Constants.ADMIN
        profile.save()
        self.assertEqual(self.user.profile.first().role, Constants.ADMIN)
    
    def test_set_user_role_fail_on_inproper_role(self):
        print("test_set_user_role_success")
        profile = Profile.objects.create(user=self.user)
        profile.role = "INVALID_ROLE"
        
        self.assertRaises(Exception, profile.save)
        self.assertEqual(self.user.profile.first().role, Constants.USER)


        
        
