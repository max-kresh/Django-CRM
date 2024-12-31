"""
Tests for models in common.
"""
from gettext import translation
from django.db import IntegrityError, transaction
from django.test import TestCase

from common.models import AppSettings

default_name = "test_setting"
default_value= "True"
default_type = "bool"


def create_setting(name, value, type):
    return AppSettings.objects.create(name=name, value=value, type=type)

class ModelTest(TestCase):
    """Test models"""

    def setUp(self):
        self.setting = create_setting(
            name=default_name, value=default_value, type=default_type)
        self.setting.save()

    def test_modify_setting_success(self):
        test_setting = AppSettings.objects.get(name="test_setting")
        self.assertEqual(test_setting.name, "test_setting")
        self.assertEqual(test_setting.value, "True")
        self.assertEqual(test_setting.type, "bool")

        test_setting.value = "False"
        test_setting.save()
        test_setting.refresh_from_db()

        self.assertEqual(test_setting.name, "test_setting")
        self.assertEqual(test_setting.value, "False")
        self.assertEqual(test_setting.type, "bool")

    def test_assign_improper_values_fails(self):
        """Test only True and False can be assigned as value if type is boolean.
        And only numbers can be assigned if type is int"""

        def modify_setting(setting, **params):
            for k, v in params.items():
                setattr(setting, k, v)
            return setting

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_setting(
                    name="False_Setting",
                    value="false_value",
                    type="bool"
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                create_setting(
                    name="False_Setting",
                    value="false_value",
                    type="bool"
                )

        test_setting = AppSettings.objects.get(name="test_setting")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                modify_setting(test_setting, **{"value": "false_value"}).save()

        test_setting.refresh_from_db()
        self.assertEqual(test_setting.value, default_value)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                modify_setting(test_setting, **{"type": "false_type"}).save()
        
        test_setting.refresh_from_db()
        self.assertEqual(test_setting.type, default_type)
                                
