"""
File: initialize_app_settings.py
Description: This file contains module with shorthand functions
             to access application's settings
Author: Maksym Kreshchyshyn
Date: 03.01.2025
Team: IT-22 Pydozen
"""

from common.models import AppSettings

def is_google_login_allowed() -> bool:
    return get_bool_setting('allow_google_login', False)

def is_login_without_invitation_allowed() -> bool:
    return get_bool_setting('allow_login_without_invitation', False)

def get_bool_setting(setting_name: str, default_value = False) -> bool:
    settings_obj = AppSettings.objects.filter(name=setting_name).first()
    if not settings_obj:
        return default_value
    return settings_obj.value == str(True)
