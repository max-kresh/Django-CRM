"""
File: mock_utils.py
Description: This file implements test utils for api (and model) tests

Author: Mithat Daglar
Date: 31.01.2025
Team: IT-22 Pydozen
"""
from django.contrib.auth import get_user_model
from django.db.models import Q

from common.models import Org, Profile, User
from common.utils import Constants, get_random_digits

def middleware_mocker(request, user, org):
        request.profile = user.profile.filter(
            Q(user=user), Q(org__name=org)).first()
        return None


def create_test_user(email = "", org_name = "Test_Org", role = Constants.USER):
    """Creates and returns a test user with a profile by using given parameters.
        email: email of the user. If there already exists a user in db with the same
                email address this function raises a ValueError. 
                If email is not provided function creates a dummy email with the format:
                <role>_<4 digit random number>@example.com
        org_name: name of the organization. If not provided "Test_Org" is used. If there
                exists an organization with the same name this function uses it. If it does 
                not exist it is created.
        role: Role of the created user. Default is USER. Uses constant valuse from Constans. 
    """
    email = email.strip()
    password = "123"
    if email:
        if User.objects.filter(email=email).exists():
            raise ValueError(f"A user with {email} already exists. "
                             f"Please provide another email or let me handle it "
                             f"by NOT specifying an email.")
    else:
        email = f"{role.lower()}_{get_random_digits(4)}@example.com"
    if role == Constants.ADMIN:
        user = get_user_model().objects.create_superuser(
            **{"email": email, "password":password}
        )
    else:
        user = get_user_model().objects.create_user(
            **{"email": email, "password": password}
        )
    user.save()
    org, _ = Org.objects.get_or_create(name=org_name)

    profile = Profile.objects.create(org=org, user=user, role=role)
    profile.save()
    print(f"{user} is created with password {password}")
    return user
