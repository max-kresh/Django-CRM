# Generated by Django 4.2.1 on 2025-03-10 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_alter_profile_alternate_phone_alter_profile_phone'),
        ('opportunity', '0003_opportunity_lead'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpportunityStageHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_stage', models.CharField(choices=[('QUALIFICATION', 'QUALIFICATION'), ('NEEDS ANALYSIS', 'NEEDS ANALYSIS'), ('VALUE PROPOSITION', 'VALUE PROPOSITION'), ('ID.DECISION MAKERS', 'ID.DECISION MAKERS'), ('PERCEPTION ANALYSIS', 'PERCEPTION ANALYSIS'), ('PROPOSAL/PRICE QUOTE', 'PROPOSAL/PRICE QUOTE'), ('NEGOTIATION/REVIEW', 'NEGOTIATION/REVIEW'), ('CLOSED WON', 'CLOSED WON'), ('CLOSED LOST', 'CLOSED LOST')], max_length=64, null=True)),
                ('new_stage', models.CharField(choices=[('QUALIFICATION', 'QUALIFICATION'), ('NEEDS ANALYSIS', 'NEEDS ANALYSIS'), ('VALUE PROPOSITION', 'VALUE PROPOSITION'), ('ID.DECISION MAKERS', 'ID.DECISION MAKERS'), ('PERCEPTION ANALYSIS', 'PERCEPTION ANALYSIS'), ('PROPOSAL/PRICE QUOTE', 'PROPOSAL/PRICE QUOTE'), ('NEGOTIATION/REVIEW', 'NEGOTIATION/REVIEW'), ('CLOSED WON', 'CLOSED WON'), ('CLOSED LOST', 'CLOSED LOST')], max_length=64)),
                ('changed_at', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='common.profile')),
                ('opportunity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stage_history', to='opportunity.opportunity')),
            ],
        ),
    ]
