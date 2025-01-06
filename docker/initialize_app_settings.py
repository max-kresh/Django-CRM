"""
File: initialize_app_settings.py
Description: This file contains Python script to initalize app
            settings when the backend starts up. Currently 
            it adds only allow_google_login settings row
            to the table if it is not already created.
Author: Mithat Daglar
Date: 31.12.2024
Team: IT-22 Pydozen
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

django.setup()

from common.models import AppSettings

def initialize():
    # Check if the entry exists
    if not AppSettings.objects.filter(name="allow_google_login").exists():
        AppSettings.objects.create(
            name="allow_google_login", 
            value="False", 
            type="bool"
        )
        print("Initialized: allow_google_login setting added.")
    else:
        print("Skipped: allow_google_login setting already exists.")

if __name__ == "__main__":
    initialize()