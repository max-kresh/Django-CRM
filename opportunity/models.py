import arrow
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from accounts.models import Account, Tags
from common.models import Org, Profile
from common.base import BaseModel
from common.utils import CURRENCY_CODES, SOURCES, STAGES
from contacts.models import Contact
from teams.models import Teams
from leads.models import Lead


class Opportunity(BaseModel):
    name = models.CharField(pgettext_lazy("Name of Opportunity", "Name"), max_length=64)
    account = models.ForeignKey(
        Account,
        related_name="opportunities",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    stage = models.CharField(
        pgettext_lazy("Stage of Opportunity", "Stage"), max_length=64, choices=STAGES
    )
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CODES, blank=True, null=True
    )
    amount = models.DecimalField(
        _("Opportunity Amount"), decimal_places=2, max_digits=12, blank=True, null=True
    )
    lead_source = models.CharField(
        _("Source of Lead"), max_length=255, choices=SOURCES, blank=True, null=True
    )
    probability = models.IntegerField(default=0, blank=True, null=True)
    contacts = models.ManyToManyField(Contact)
    closed_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="oppurtunity_closed_by",
    )
    # closed_on = models.DateTimeField(blank=True, null=True)
    closed_on = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(
        Profile, related_name="opportunity_assigned_to"
    )
    is_active = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tags, blank=True)
    teams = models.ManyToManyField(Teams, related_name="oppurtunity_teams")
    org = models.ForeignKey(
        Org,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="oppurtunity_org",
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.RESTRICT,
        blank=True,
        null=True)

    class Meta:
        verbose_name = "Opportunity"
        verbose_name_plural = "Opportunities"
        db_table = "opportunity"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}"
    
    @property
    def created_on_arrow(self):
        return arrow.get(self.created_at).humanize()

    @property
    def get_team_users(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        return Profile.objects.filter(id__in=team_user_ids)

    @property
    def get_team_and_assigned_users(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        assigned_user_ids = list(self.assigned_to.values_list("id", flat=True))
        user_ids = team_user_ids + assigned_user_ids
        return Profile.objects.filter(id__in=user_ids)

    @property
    def get_assigned_users_not_in_teams(self):
        team_user_ids = list(self.teams.values_list("users__id", flat=True))
        assigned_user_ids = list(self.assigned_to.values_list("id", flat=True))
        user_ids = set(assigned_user_ids) - set(team_user_ids)
        return Profile.objects.filter(id__in=list(user_ids))

    @property
    def get_contacts_list(self):
        return list(self.contacts.all())


class OpportunityStageHistory(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="stage_history")
    old_stage = models.CharField(max_length=64, choices=STAGES, null=True)
    new_stage = models.CharField(max_length=64, choices=STAGES)
    changed_by = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.opportunity.name} changed from {self.old_stage} to {self.new_stage}"
