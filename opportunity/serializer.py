from rest_framework import serializers

from accounts.models import Tags
from accounts.serializer import AccountSerializer
from common.serializer import AttachmentsSerializer, ProfileSerializer,UserSerializer
from contacts.serializer import ContactSerializer
from opportunity.models import Opportunity, OpportunityStageHistory
from teams.serializer import TeamsSerializer
from leads.serializer import LeadSerializer


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "slug")


class OpportunitySerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    closed_by = ProfileSerializer()
    created_by = UserSerializer()
    tags = TagsSerializer(read_only=True, many=True)
    assigned_to = ProfileSerializer(read_only=True, many=True)
    contacts = ContactSerializer(read_only=True, many=True)
    teams = TeamsSerializer(read_only=True, many=True)
    opportunity_attachment = AttachmentsSerializer(read_only=True, many=True)
    lead = LeadSerializer(read_only=True, many=False)

    class Meta:
        model = Opportunity
        # fields = ‘__all__’
        fields = (
            "id",
            "name",
            "stage",
            "currency",
            "amount",
            "lead_source",
            "probability",
            "contacts",
            "closed_by",
            "closed_on",
            "description",
            "assigned_to",
            "created_by",
            "created_at",
            "is_active",
            "tags",
            "opportunity_attachment",
            "teams",
            "created_on_arrow",
            "account",
            "lead"
        )


class OpportunityCreateSerializer(serializers.ModelSerializer):
    probability = serializers.IntegerField(max_value=100)
    closed_on = serializers.DateField
    created_by = UserSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        if request_obj:
            self.org = request_obj.profile.org

    def validate_name(self, name):
        if self.instance:
            if (
                Opportunity.objects.filter(name__iexact=name, org=self.org)
                .exclude(id=self.instance.id)
                .exists()
            ):
                raise serializers.ValidationError(
                    "Opportunity already exists with this name"
                )

        else:
            if Opportunity.objects.filter(name__iexact=name, org=self.org).exists():
                raise serializers.ValidationError(
                    "Opportunity already exists with this name"
                )
        return name

    class Meta:
        model = Opportunity
        fields = (
            "name",
            "account",
            "stage",
            "currency",
            "amount",
            "lead_source",
            "probability",
            "closed_on",
            "description",
            "created_by",
            "is_active",
            "org",
            "lead"
        )
class OpportunityPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ("stage", )
class OpportunityStageHistorySerializer(serializers.ModelSerializer):
    changed_by = ProfileSerializer()
    class Meta:
        model = OpportunityStageHistory
        fields = (
            "opportunity",
            "old_stage",
            "new_stage",
            "changed_by",
            "changed_at",
        )



class OpportunityDetailEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
    opportunity_attachment = serializers.FileField()

class OpportunityCommentEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
