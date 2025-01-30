from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.tests.factories import (
    OrgFactory,
    UserFactory,
    ProfileFactory,
    AddressFactory,
)
from .factories import ContactFactory
from rest_framework_simplejwt.tokens import RefreshToken
class ContactsListViewFilteringTest(APITestCase):
    def setUp(self):
        # Create Organization
        self.org1 = OrgFactory()
        self.org2 = OrgFactory()
        # Create a user and profile
        self.example_user = UserFactory(email="example")
        self.example_user.set_password("examplepass")
        self.example_user.save()
        # create token for user
        refresh = RefreshToken.for_user(self.example_user)
        self.access_token1 = str(refresh.access_token)
        self.refresh_token1 = str(refresh)
        self.example_profile = ProfileFactory(
            user=self.example_user,
            org=self.org1,
            role="USER",  
            is_active=True
        )
        # Create another user and profile
        self.example_user2 = UserFactory(email="example2")
        self.example_user2.set_password("examplepass")
        self.example_user2.save()
        # create token for user
        refresh2 = RefreshToken.for_user(self.example_user2)
        self.access_token2 = str(refresh2.access_token)
        self.refresh_token2 = str(refresh2)
        self.example_profile2 = ProfileFactory(
            user=self.example_user2,
            org=self.org2,
            role="USER",  
            is_active=True
        )

        # Create addresses
        self.address1 = AddressFactory(city="CityA", postcode="1000AB", country="US")
        self.address2 = AddressFactory(city="CityB", postcode="2000CD", country="US")

        # Create contacts
        self.contact1 = ContactFactory(
            first_name="John",
            last_name="Doe",
            primary_email="john@example.com",
            mobile_number="+1234567890",
            address=self.address1,
            org=self.org1,
            category="Account"  
        )
        # Assign this contact to the  profile1
        self.contact1.assigned_to.add(self.example_profile)

        self.contact2 = ContactFactory(
            first_name="Jane",
            last_name="Smith",
            primary_email="jane@example.com",
            mobile_number="+9876543210",
            address=self.address2,
            org=self.org2,
            category="Lead"
        )
        # Assign this contact to the  profile2
        self.contact2.assigned_to.add(self.example_profile2)

        self.url = reverse("common_urls:api_contacts:contacts-list")

   

    def test_filter_by_email(self):
        """
        Filter contacts by email (primary or secondary).
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token1)
        params = {"email": self.contact1.primary_email}
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["primary_email"], self.contact1.primary_email)

    def test_filter_by_phone(self):
        """
        Filter contacts by phone (mobile_number or secondary_number).
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token1)

        # also give a secondary_number
        self.contact1.secondary_number = "+9999999999"
        self.contact1.save()

        # Filter by partial phone in contact1
        params = {"phone": str(self.contact1.mobile_number)[2:8]}  # partial match [2:8] = "123456"
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["id"], str(self.contact1.id))

        # Filter by partial phone in contact1's secondary_number
        params = {"phone": "99999999"}
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["id"], str(self.contact1.id))

    def test_filter_by_category(self):
        """
        Filter contacts by category (must be one of CONTACT_CATEGORIES).
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token1)
        params = {"category": self.contact1.category}  
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["id"], str(self.contact1.id))
        self.assertEqual(response.data["contact_obj_list"][0]["category"], self.contact1.category)
    
    def test_filter_by_wrong_category_name(self):
        """
        Filter contacts by wrong category name. It should ignore category filter and return all contacts.
        """
        # create another contact with same orgaization and same assigned to user
        second_contact = ContactFactory(
            address=self.address2,
            org=self.org1,
            category="Account"  
        )
        second_contact.assigned_to.add(self.example_profile)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token1)
        params = {"category": "Customer"}  
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 2) # 2 contacts within same org and same assigned to user

    def test_filter_by_name(self):
        """
        Filter contacts by partial match in first_name.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token1)
        params = {"name": self.contact1.first_name[0:3]}  # partial for "John"
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["first_name"], self.contact1.first_name)

    def test_filter_by_postcode_city(self):
        """
        Filter by postcode or city in address.
        """
        # credentials for user1
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token1)

        # City filter
        params = {"city": "CityA"}
        response = self.client.get(self.url, params, headers={'org': self.org1.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["id"], str(self.contact1.id))
        
        # credentials for user2
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token2)
        # Postcode filter
        params = {"postcode": "2000CD"}
        response = self.client.get(self.url, params, headers={'org': self.org2.name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["contacts_count"], 1)
        self.assertEqual(response.data["contact_obj_list"][0]["id"], str(self.contact2.id))