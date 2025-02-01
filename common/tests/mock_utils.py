"""
File: mock_utils.py
Description: This file implements test utils for api (and model) tests

Author: Mithat Daglar
Date: 31.01.2025
Team: IT-22 Pydozen
"""

from unittest.mock import patch
from functools import wraps
from django.contrib.auth import get_user_model
from random import randint

from common.models import Profile, Org

from common.utils import Constants


def mock_crm_middleware(user_field_name):
    """Decorator to mock GetProfileAndOrg middleware in test cases with a given user.
       user_field_name: field name on the user making the http request exp: if you have 
       a field in your test class with an name admin_user pass this name as a string. 
    """

    def mock_middleware_call(request, user):
        """Adds user profile into request. This function is called when a http
        request is sent by a mocking test function before the request reaches to 
        the endpoint."""
        
        request.profile = user.profile.first() 
        return request

    def decorator(test_func):
        @patch("common.middleware.get_company.GetProfileAndOrg")
        @wraps(test_func)
        def wrapper(self, mock_middleware, *args, **kwargs):
            current_user = getattr(self, user_field_name)
            if not current_user:
                raise ValueError(f"A field with name {user_field_name} could not be found. 
                                 Crm middleware can not be mocked with this value.")
            self.client.force_authenticate(current_user)
            mock_middleware.side_effect = lambda request: mock_middleware_call(request, current_user)
            
            return test_func(self, *args, **kwargs)  
        
        return wrapper

    return decorator


def get_random_digits(n_of_digits):
    """Returns a string of length n_of_digits composed of random numbers
    between 0 and 9 (both are inclusive)"""
    return ("".join([str(randint(0, 9)) for i in range(0, n_of_digits)]))

def create_test_user(org_name = "Test_Org", role = Constants.USER):
    """Creates and returns a test user with a profile by using given parameters."""
    if role == Constants.ADMIN:
        user = get_user_model().objects.create_superuser(
            **{"email":f"admin_{get_random_digits(4)}@example.com", "password":"password123"}
        )
    else:
        user = get_user_model().objects.create_user(
            **{"email":f"{role.lower()}_{get_random_digits(4)}@example.com", "password":"password123"}
        )
    user.save()
    org, _ = Org.objects.get_or_create(name=org_name)

    profile = Profile.objects.create(org=org, user=user, role=role)
    profile.save()
    return user
