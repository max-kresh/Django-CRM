from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch


from common.tests.factories import (
    OrgFactory,
    UserFactory,
    ProfileFactory,
    AddressFactory,
)
from rest_framework_simplejwt.tokens import RefreshToken
class UserListViewTests(APITestCase):
    def setUp(self):
        # Create Organization
        self.org1 = OrgFactory()
        # Create an user
        self.admin_user = UserFactory(email="admin")
        self.admin_user.set_password("adminpass")
        self.admin_user.save()
        # Create Admin profile
        self.admin_profile = ProfileFactory(
            user=self.admin_user,
            org=self.org1,
            role="ADMIN",  
            is_active=True
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_access_token = str(refresh.access_token)

    # Create normal user and profile
        # Create an user
        self.example_user = UserFactory(email="example")
        self.example_user.set_password("examplepass")
        self.example_user.save()
        # Create example profile
        self.example_profile = ProfileFactory(
            user=self.example_user,
            org=self.org1,
            role="USER",  
            is_active=True
        )
        example_refresh = RefreshToken.for_user(self.example_user)
        self.example_user_access_token = str(example_refresh.access_token)
    
        


        self.example_user_data = {
        "email": "example@gmail.com",
        "role": "USER",
        "phone": "+31685753609",
        "address_line": "Main String street",
        "street": "main string",
        "city": "Amstring",
        "state": "North String",
        "pincode": "1059ER",
        "country": "NL",
        }

        self.url = reverse("common_urls:api_common:users-list")
    # Add user to organization tests
    @patch("common.views.send_email_to_new_user.delay")
    def test_add_user_to_org_as_admin(self,mock_task):
        """
        Add user to organization as organization admin
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.post(self.url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_task.assert_called_once()

    
    def test_add_user_to_org_as_user_results_in_403(self):
        """
        Regular organization user (non-admin) 
        cannot add another user to the organization.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        response = self.client.post(self.url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_user_to_org_as_non_orgazinational_admin_results_in_403(self):
        """
        User who is not an admin of the organization cannot add another user to the organization.
        """
        org2 = OrgFactory()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        response = self.client.post(self.url, data=self.example_user_data, format="json", headers={'org': org2.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_add_user_to_org_as_unauthenticated_user_results_in_401(self):  
        """
        Unauthenticated user cannot add another user to the organization.
        """
        response = self.client.post(self.url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    # # Get users list tests
        # def test_get_users_list_as_admin(self):
        #     """
        #     Admin can get the list of users in the organization.
        #     """
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        #     response = self.client.get(self.url, headers={'org': self.org1.name})
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(response.data["active_users"]["active_users_count"], 2)
        
        # def test_get_users_list_as_user_results_in_403(self):
        #     """
        #     Regular organization user (non-admin) cannot get the list of users in the organization.
        #     """
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        #     response = self.client.get(self.url, headers={'org': self.org1.name})
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        #     # self.assertEqual(response.data["active_users"]["active_users_count"], 3)
        
        # def test_get_user_as_sales_manager(self):
        #     """
        #     Sales Manager can get the list of users in the organization.
        #     """
        #     self.example_profile.role = "SALES_MANAGER"
        #     self.example_profile.save()
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        #     response = self.client.get(self.url, headers={'org': self.org1.name})
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(response.data["active_users"]["active_users_count"], 2)
        
        # def test_get_users_list_as_unauthenticated_user_results_in_401(self):
        #     """
        #     Unauthenticated user cannot get the list of users in the organization.
        #     """
        #     response = self.client.get(self.url, headers={'org': self.org1.name})
        #     print(response)
        #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # def test_get_users_list_as_non_orgazinational_admin_results_in_403(self):
        #     """
        #     User who is not an admin of the organization cannot get the list of users in the organization.
        #     """
        #     org2 = OrgFactory()
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        #     response = self.client.get(self.url, headers={'org': org2.name})
        #     print(response)
        #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # # Get users by filter tests
        # def test_get_users_as_admin_by_filtering_role(self):
        #     """
        #     Admin can get the list of users in the organization by filtering role.
        #     """
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        #     response = self.client.get(self.url + "?role=USER", headers={'org': self.org1.name})
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(response.data["active_users"]["active_users_count"], 1)
        #     self.assertEqual(response.data["active_users"]["active_users"][0]["id"], str(self.example_profile.id))
        
        # def test_get_users_as_admin_by_filtering_status(self):
        #     """
        #     Admin can get the list of users in the organization by filtering status.
        #     """
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        #     response = self.client.get(self.url + "?is_active=True", headers={'org': self.org1.name})
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(response.data["active_users"]["active_users_count"], 2)
        
        # def test_get_users_as_admin_by_filtering_email(self):
        #     """
        #     Admin can get the list of users in the organization by filtering email.
        #     """
        #     self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        #     response = self.client.get(self.url + f"?email={self.example_user.email}", headers={'org': self.org1.name})
        #     print(response.data)
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertEqual(response.data["active_users"]["active_users"][0]["user_details"]["email"], self.example_user.email)
        
class UserDetailViewTests(APITestCase):
    def setUp(self):
        # Create Organization
        self.org1 = OrgFactory()
        # Create an user
        self.admin_user = UserFactory(email="admin")
        self.admin_user.set_password("adminpass")
        self.admin_user.save()
        # Create Admin profile
        self.admin_profile = ProfileFactory(
            user=self.admin_user,
            org=self.org1,
            role="ADMIN",  
            is_active=True
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_access_token = str(refresh.access_token)

    # Create normal user and profile
        # Create an user
        self.example_user = UserFactory(email="example")
        self.example_user.set_password("examplepass")
        self.example_user.save()
        # Create example profile
        self.example_profile = ProfileFactory(
            user=self.example_user,
            org=self.org1,
            role="USER",  
            is_active=True
        )
        example_refresh = RefreshToken.for_user(self.example_user)
        self.example_user_access_token = str(example_refresh.access_token)
    
        self.url=reverse("common_urls:api_common:user-detail", kwargs={"pk": self.example_profile.id})
        self.example_user_data = {
        "email": "example@gmail.com",
        "role": "USER",
        "phone": "+31685753609",
        "address_line": "Main String street",
        "street": "main string",
        "city": "Amstring",
        "state": "North String",
        "pincode": "1059ER",
        "country": "NL",
        }
    # Get user detail tests
    def test_get_user_detail_as_admin(self):
        """
        Admin can get the detail of a user in the organization.se
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(self.url, headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["profile_obj"]["user_details"]["email"], self.example_user.email)
    
    def test_get_user_from_another_organization_as_admin_results_in_403(self):
        """
        Admin of an organization cannot get the detail of a user in another organization.
        """
        org2 = OrgFactory()
        new_user = UserFactory(email="new_user")
        new_user.set_password("new_user_pass")
        new_user.save()
        new_profile = ProfileFactory(
            user=new_user,
            org=org2,
            role="USER",  
            is_active=True
        )
        url=reverse("common_urls:api_common:user-detail", kwargs={"pk": new_profile.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.get(url, headers={'org': org2.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    
    def test_get_own_user_detail_as_user(self):
        """
        User can get the detail of their own profile.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        response = self.client.get(self.url, headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["profile_obj"]["user_details"]["email"], self.example_user.email)

    def test_get_user_detail_as_user_results_in_403(self):
        """
        Regular organization user (non-admin) cannot get the detail of another user in the organization.
        """
        # Create a regular user and profile
        new_user = UserFactory(email="new_user")
        new_user.set_password("new_user_pass")
        new_user.save()
        new_profile = ProfileFactory(
            user=new_user,
            org=self.org1,
            role="USER",  
            is_active=True
        )
        new_profile.save()
        new_refresh = RefreshToken.for_user(new_user)
        new_user_access_token = str(new_refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_user_access_token)
        response = self.client.get(self.url, headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_user_detail_as_unauthenticated_user_results_in_401(self):
        """
        Unauthenticated user cannot get the detail of a user in the organization.
        """
        response = self.client.get(self.url, headers={'org': self.org1.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # Update user detail tests
    def test_update_user_detail_as_admin(self):
        """
        Admin can update the detail of a user in the organization.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.put(self.url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_user_own_profile_as_user(self):
        """
        User can update their own profile.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        response = self.client.put(self.url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_user_detail_from_another_organization_as_admin_results_in_403(self):
        """
        Admin of an organization cannot update the detail of a user in another organization.
        """
        org2 = OrgFactory()
        new_user = UserFactory(email="new_user")
        new_user.set_password("new_user_pass")
        new_user.save()
        new_profile = ProfileFactory(
            user=new_user,
            org=org2,
            role="USER",  
            is_active=True
        )
        new_profile.save()
        new_refresh = RefreshToken.for_user(new_user)
        new_user_access_token = str(new_refresh.access_token)
        url=reverse("common_urls:api_common:user-detail", kwargs={"pk": new_profile.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.put(url, data=self.example_user_data, format="json", headers={'org': org2.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_a_user_detail_as_user_results_in_403(self):
        """
        Regular organization user (non-admin) cannot update the detail of another user in the organization.
        """
        # Create a regular user and profile
        new_user = UserFactory(email="new_user")
        new_user.set_password("new_user_pass")
        new_user.save()
        new_profile = ProfileFactory(
            user=new_user,
            org=self.org1,
            role="USER",  
            is_active=True
        )
        new_profile.save()
        new_refresh = RefreshToken.for_user(new_user)
        new_user_access_token = str(new_refresh.access_token)
        url=reverse("common_urls:api_common:user-detail", kwargs={"pk": new_profile.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + new_user_access_token)
        response = self.client.put(url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_user_detail_as_unauthenticated_user_results_in_401(self):
        """
        Unauthenticated user cannot update the detail of a user in the organization.
        """
        response = self.client.put(self.url, data=self.example_user_data, format="json", headers={'org': self.org1.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_user_detail_with_invalid_address_data_results_in_400(self):
        """
        Update user detail with invalid data.
        """
        address_data = {"country": "NLD"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.put(self.url, data=address_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_user_detail_with_invalid_email_results_in_400(self):
        """
        Update user detail with invalid email.
        """
        email_data = {"email": "invalid_email"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.put(self.url, data=email_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_user_detail_with_invalid_phone_results_in_400(self):
        """
        Update user detail with invalid phone.
        """
        phone_data = {"phone": "invalid_phone"}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.put(self.url, data=phone_data, format="json", headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # Delete user tests
    @patch("common.views.send_email_user_delete.delay")
    def test_delete_user_as_admin(self, mock_task):
        """
        Admin can delete a user in the organization.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.delete(self.url, headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_task.assert_called_once()
    
    def test_delete_user_from_another_organization_as_admin_results_in_403(self):
        """
        Admin of an organization cannot delete a user in another organization.
        """
        org2 = OrgFactory()
        new_user = UserFactory(email="new_user")
        new_user.set_password("new_user_pass")
        new_user.save()
        new_profile = ProfileFactory(
            user=new_user,
            org=org2,
            role="USER",  
            is_active=True
        )
        new_profile.save()
        new_refresh = RefreshToken.for_user(new_user)
        new_user_access_token = str(new_refresh.access_token)
        url=reverse("common_urls:api_common:user-detail", kwargs={"pk": new_profile.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_access_token)
        response = self.client.delete(url, headers={'org': org2.name})
        print(response)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_user_as_user(self):
        """
        User cannot delete any profile.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.example_user_access_token)
        response = self.client.delete(self.url, headers={'org': self.org1.name})
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)