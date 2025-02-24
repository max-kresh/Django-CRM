"""
File: crm_permissions.py
Description: This file implements permissions based on user roles.

Author: Mithat Daglar
Date: 07.01.2025
Team: IT-22 Pydozen
"""

from rest_framework.permissions import BasePermission
from common.utils import Constants


def get_user_role(request):
    """Returns the role of the user if exists, otherwise returns "NO_ROLE_FOR_USER"."""
    try:
        role = request.profile.role
    except AttributeError:
        role = "NO_ROLE_FOR_USER"
    finally:
        return role

# Role-based permissions
class IsAdmin(BasePermission):
    """Checks if user is ADMIN"""    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = get_user_role(request) 
        return role == (Constants.ADMIN or request.user.is_superuser)

class IsSalesManager(BasePermission):
    """Checks if user is SALES_MANAGER"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        return role == Constants.SALES_MANAGER

class IsSalesRep(BasePermission):
    """Checks if user is SALES_REPRESENTATIVE"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        return role == Constants.SALES_REPRESENTATIVE

class IsUser(BasePermission):
    """Checks if user is USER"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role = get_user_role(request)
        return role == Constants.USER


# Role and http method-based permissions
class CanListUsers(BasePermission):
    """Allows GET requests for Admin and Sales Manager roles."""
    
    def has_permission(self, request, view):
        # Check if the user has the required role and the request method is safe
        if not request.user.is_authenticated:
            return False
        return (
            (IsAdmin().has_permission(request, view) or IsSalesManager().has_permission(request, view))
            and request.method in ["GET"]
        )


class CanModifyUsers(BasePermission):
    """Allows POST, PUT, or DELETE requests for Admin role only."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check if the user is an Admin and the request method is for modification
        return IsAdmin().has_permission(request, view) and request.method in Constants.HTTP_WRITE_METHODS
