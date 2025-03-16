from rest_framework import serializers

from common.models import Address, Comment
from common.serializer import (
    AttachmentsSerializer,
    BillingAddressSerializer,
    OrganizationSerializer,
    ProfileSerializer,
)
from common.utils import Constants
from contacts.models import Contact
from teams.serializer import TeamsSerializer

PROSPECT = "Prospect"
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
    created_by_email = serializers.SerializerMethodField()

    def get_country(self, obj):
        return obj.get_country_display()
    
    def get_created_by_email(self, obj):
        return obj.created_by.email

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
            "category",
            "created_by_email"
        )


class CreateContactSerializer(serializers.ModelSerializer):
    address = BillingAddressSerializer(required=False)
    is_prospect = serializers.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        request_obj = kwargs.pop("request_obj", None)
        super().__init__(*args, **kwargs)
        if request_obj:
            self.org = request_obj.profile.org
            self.user_role = request_obj.profile.role        
    
    
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
            "is_prospect",
        )
    

    def create(self, validated_data):
        address_data = validated_data.pop("address", None)
        if address_data:
            address_instance, created = Address.objects.get_or_create(**address_data)
            validated_data["address"] = address_instance

        if hasattr(validated_data, "is_prospect"):
            prospect_data = validated_data.pop("is_prospect")
            # Category of a contact is not a 'basic' contact info. Thus regular
            #   users can not set it.
            if self.user_role is not Constants.USER:
                validated_data["category"] = PROSPECT if prospect_data else None          
            

        contact_instance = Contact.objects.create(**validated_data)
        
        return contact_instance

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        if address_data:
            address_instance, created = Address.objects.get_or_create(**address_data)
            instance.address = address_instance
            instance.save()
        
        # Updating the category conditions:
        # 1. Category of a contact is not a 'basic' contact info. Thus regular
        #   users can not set it.
        # 2. Do not update the category if is_prospect field is not provided
        # 3. If a contact has already a category different than 
        #   'Prospect' (e.g. 'Lead') do not allow it be set as 'Prospect'
        if hasattr(validated_data, "is_prospect") and validated_data.get('is_prospect') is not None:
            prospect_data = validated_data.pop("is_prospect")
            if (self.user_role is not Constants.USER 
                and prospect_data is not None
                and instance.category in [PROSPECT, None]):
                    validated_data["category"] = PROSPECT if prospect_data else None

        return super().update(instance, validated_data)

    

class ContactAttachmentSwaggerSerializer(serializers.Serializer):
    contact_attachment = serializers.FileField()

class ContactCommentEditSwaggerSerializer(serializers.Serializer):
    comment = serializers.CharField()

class ContactCommentSerializer(serializers.ModelSerializer):
    commented_by_email = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "comment",
            "commented_on",
            "commented_by",
            "contact",
            "commented_by_email",  
        )

    def get_commented_by_email(self, obj):
        return obj.commented_by.user.email if obj.commented_by and obj.commented_by.user else ''