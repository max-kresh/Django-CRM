import common.models
import uuid
from django.db import migrations, models

def insert_settings(apps, schema_editor):
    AppSettings = apps.get_model('common', 'AppSettings')
    if not AppSettings.objects.filter(name="allow_google_login").exists():
        AppSettings.objects.create(
            name="allow_google_login", 
            value="False", 
            type="bool"
        )
    if not AppSettings.objects.filter(name="allow_login_without_invitation").exists():
        AppSettings.objects.create(
            name="allow_login_without_invitation", 
            value="False", 
            type="bool"
        )

class Migration(migrations.Migration):

    dependencies = [
        ('common', '0010_app_settings_table'),
    ]

    operations = [
        migrations.RunPython(insert_settings),
    ]
