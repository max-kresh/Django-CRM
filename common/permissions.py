"""
File: permissions.py
Description: This file implements permissions based on user roles.

Author: Mithat Daglar
Date: 07.01.2025
Team: IT-22 Pydozen
"""

from rest_framework.permissions import BasePermission
from common.utils import Constants


def get_user_role(user):
    """Returns the role of the user if exists, otherwise returns "NO_ROLE_FOR_USER"."""
    try:
        role = user.profile.first().role
    except AttributeError:
        role = "NO_ROLE_FOR_USER"
    finally:
        return role

# Role-based permissions
class IsAdmin(BasePermission):
    """Checks if user is ADMIN"""    
    def has_permission(self, request, view):
        role = get_user_role(request.user) 
        return role == (Constants.ADMIN or request.user.is_superuser)

class IsSalesManager(BasePermission):
    """Checks if user is SALES_MANAGER"""
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        return role == Constants.SALES_MANAGER

class IsSalesRep(BasePermission):
    """Checks if user is SALES_REPRESENTATIVE"""
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        return role == Constants.SALES_REPRESENTATIVE

class IsUser(BasePermission):
    """Checks if user is USER"""
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        return role == Constants.USER

# Role and http method-based permissions
class CanListUsers(BasePermission):
    """Checks if the user can make GET request to user-list url"""
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        return role in [Constants.ADMIN, Constants.SALES_MANAGER] and request.method in ["GET"]

class CanModifyUsers(BasePermission):
    """Checks if the user can make POST, PUT or DELETE request to user-list url"""
    def has_permission(self, request, view):
        role = get_user_role(request.user)
        return role == Constants.ADMIN and request.method in ["POST", "PUT", "DELETE"]