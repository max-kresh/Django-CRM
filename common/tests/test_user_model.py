from django.contrib.auth import get_user_model
from django.test import TestCase
from common.models import User, Profile

class ModelTest(TestCase):
    """Tests for user roles"""

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="password")
        

    def test_set_user_role_success(self):
        print("test_set_user_role_success")
        profile = Profile.objects.create(user=self.user)
        profile.role = "ADMIN"
        profile.save()
        self.assertEqual(self.user.profile.first().role, "ADMIN")
    
    def test_set_user_role_fail_on_inproper_role(self):
        print("test_set_user_role_success")
        profile = Profile.objects.create(user=self.user)
        profile.role = "INVALID_ROLE"
        
        self.assertRaises(Exception, profile.save)
        self.assertEqual(self.user.profile.first().role, "USER")


        
        
