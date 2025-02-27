from rest_framework import serializers

from common.models import Address
from common.serializer import (
    AttachmentsSerializer,
    BillingAddressSerializer,
    OrganizationSerializer,
    ProfileSerializer,
)
from contacts.models import Contact
from teams.serializer import TeamsSerializer


class ContactSerializer(serializers.ModelSerializer):
    teams = TeamsSerializer(read_only=True, many=True)
    assigned_to = ProfileSerializer(read_only=True, many=True)
    address = BillingAddressSerializer(read_only=True)
    get_team_users = ProfileSerializer(read_only=True, many=True)
    get_team_and_assigned_users = ProfileSerializer(read_only=True, many=True)
    get_assigned_users_not_in_teams = ProfileSerializer(read_only=True, many=True)
    contact_attachment = AttachmentsSerializer(read_only=True, many=True)
    date_of_birth = serializers.DateField()
    org = OrganizationSerializer()
    country = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.get_country_display()

    class Meta:
        model = Contact
        fields = (
            "id",
            "salutation",
            "first_name",
            "last_name",
            "date_of_birth",
            "organization",
            "title",
            "primary_email",
            "secondary_email",
            "mobile_number",
            "secondary_number",
            "department",
            "country",
            "language",
            "do_not_call",
            "address",
            "description",
            "linked_in_url",
            "facebook_url",
            "twitter_username",
            "contact_attachment",
            "assigned_to",
            "created_by",
            "created_at",
            "is_active",
            "teams",
            "created_on_arrow",
            "get_team_users",
            "get_team_and_assigned_users",
            "get_assigned_users_not_in_teams",
            "org",
            "category"
        )


class CreateContactSerializer(serializers.ModelSerializer):
    address = BillingAddressSerializer(required=False)
    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        if request_obj:
            self.org = request_obj.profile.org
    
    
    class Meta:
        model = Contact
        fields = (
            "salutation",
            "first_name",
            "last_name",
            "organization",
            "title",
            "primary_email",
            "secondary_email",
            "mobile_number",
            "secondary_number",
            "department",
            "country",
            "language",
            "do_not_call",
            "address",
            "description",
            "linked_in_url",
            "facebook_url",
            "twitter_username",
        )

    def create(self, validated_data):
        address_data = validated_data.pop("address", None)
        if address_data:
            address_instance, created = Address.objects.get_or_create(**address_data)
            validated_data["address"] = address_instance
        contact_instance = Contact.objects.create(**validated_data)
        
        return contact_instance

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        if address_data:
            address_instance, created = Address.objects.get_or_create(**address_data)
            instance.address = address_instance
            instance.save()

        return super().update(instance, validated_data)

    

class ContactDetailEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
    contact_attachment = serializers.FileField()

class ContactCommentEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()
