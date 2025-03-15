# Generated by Django 4.2.1 on 2025-03-14 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_merge_20250128_1156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='category',
            field=models.CharField(choices=[('Prospect', 'Prospect'), ('Lead', 'Lead'), ('Opportunity', 'Opportunity'), ('Account', 'Account')], max_length=11, null=True),
        ),
    ]
