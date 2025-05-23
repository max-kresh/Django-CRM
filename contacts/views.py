import datetime
import json

from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.models import Attachments, Comment, Profile
from common.serializer import (
    AttachmentsSerializer,
    BillingAddressSerializer,
    CommentSerializer,
)
from common.utils import CONTACT_CATEGORIES, COUNTRIES, Constants

#from common.external_auth import CustomDualAuthentication
from contacts import swagger_params1
from contacts.models import Contact, Profile
from contacts.serializer import *
from contacts.tasks import send_email_to_assigned_user
from tasks.serializer import TaskSerializer
from teams.models import Teams


class ContactsListView(APIView, LimitOffsetPagination):
    #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)
    model = Contact

    def get_context_data(self, **kwargs):
        params = self.request.query_params
        queryset = self.model.objects.filter(org=self.request.profile.org).order_by("-id")
        if (self.request.profile.role not in [Constants.ADMIN, Constants.SALES_MANAGER] 
            and not self.request.profile.is_admin):
            queryset = queryset.filter(
                Q(assigned_to__in=[self.request.profile])
                | Q(created_by=self.request.profile.user)
            ).distinct()

        if params:
            if params.get("email"):
                queryset = queryset.filter(Q(primary_email__icontains=params.get("email")) | Q(secondary_email__icontains=params.get("email")))
            if params.get("phone"):
                queryset = queryset.filter(Q(mobile_number__icontains=params.get("phone")) | Q(secondary_number__icontains=params.get("phone")))
            if params.get("category") and params.get("category") in CONTACT_CATEGORIES:
                queryset = queryset.filter(category__icontains=params.get("category"))
            if params.get("name"):
                queryset = queryset.filter(first_name__icontains=params.get("name"))
            if params.get("postcode"):
                queryset = queryset.filter(address__postcode__icontains=params.get("postcode"))
            if params.get("city"):
                queryset = queryset.filter(address__city__icontains=params.get("city"))
            
            
            
            if params.getlist("assigned_to"):
                queryset = queryset.filter(
                    assigned_to__id__in=params.get("assigned_to")
                ).distinct()

        context = {}
        results_contact = self.paginate_queryset(
            queryset.distinct(), self.request, view=self
        )
        contacts = ContactSerializer(results_contact, many=True).data
        if results_contact:
            offset = queryset.filter(id__gte=results_contact[-1].id).count()
            if offset == queryset.count():
                offset = None
        else:
            offset = 0
        context["per_page"] = 10
        page_number = (int(self.offset / 10) + 1,)
        context["page_number"] = page_number
        context.update({"contacts_count": self.count, "offset": offset})
        context["contact_obj_list"] = contacts
        users = Profile.objects.filter(is_active=True, org=self.request.profile.org).values(
            "id", "user__email"
        )
        context["users"] = users

        return context

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.contact_list_get_params
    )
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return Response(context)

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params,request=CreateContactSerializer
    )
    def post(self, request, *args, **kwargs):
        params = request.data
        contact_serializer = CreateContactSerializer(data=params, request_obj=request)

        data = {}
        if not contact_serializer.is_valid():
            data["contact_errors"] = contact_serializer.errors
        if data:
            return Response(
                {"error": True, "errors": data},
                status=status.HTTP_400_BAD_REQUEST,
            )
        contact_obj = contact_serializer.save(date_of_birth=params.get("date_of_birth"))
        contact_obj.org = request.profile.org
        contact_obj.save()

        if params.get("teams"):
            teams_list = params.get("teams")
            teams = Teams.objects.filter(id__in=teams_list, org=request.profile.org)
            contact_obj.teams.add(*teams)

        if params.get("assigned_to"):
            assinged_to_list = params.get("assigned_to")
            profiles = Profile.objects.filter(id__in=assinged_to_list, org=request.profile.org)
            contact_obj.assigned_to.add(*profiles)

        recipients = list(contact_obj.assigned_to.all().values_list("id", flat=True))
        send_email_to_assigned_user.delay(
            recipients,
            contact_obj.id,
        )

        if request.FILES.get("contact_attachment"):
            attachment = Attachments()
            attachment.created_by = request.profile.user
            attachment.file_name = request.FILES.get("contact_attachment").name
            attachment.contact = contact_obj
            attachment.attachment = request.FILES.get("contact_attachment")
            attachment.save()
        return Response(
            {"error": False, "message": "Contact created successfully", "contact": ContactSerializer(contact_obj).data},
            status=status.HTTP_200_OK,
        )


class ContactDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    model = Contact

    def get_object(self, pk, org):
        return get_object_or_404(Contact, pk=pk, org=org)

    @extend_schema(
         tags=["Contacts"], parameters=swagger_params1.organization_params,request=CreateContactSerializer
    )
    def put(self, request, pk, format=None):
        data = request.data
        contact_obj = self.get_object(pk=pk, org=request.profile.org)
        if contact_obj.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company does not match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        contact_serializer = CreateContactSerializer(
            data=data, instance=contact_obj, request_obj=request
        )
        data = {}
        if not contact_serializer.is_valid():
            data["contact_errors"] = contact_serializer.errors
        if data:
            data["error"] = True
            return Response(
                data,
                status=status.HTTP_400_BAD_REQUEST,
            )

        if contact_serializer.is_valid():
            if (
                self.request.profile.role not in [Constants.ADMIN, Constants.SALES_MANAGER]
                and not self.request.profile.is_admin
            ):
                if not (
                    (self.request.profile.user == contact_obj.created_by)
                    or (self.request.profile.user in contact_obj.assigned_to.all())
                ):
                    return Response(
                        {
                            "error": True,
                            "errors": "You do not have Permission to perform this action",
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            contact_obj = contact_serializer.save(
                date_of_birth=data.get("date_of_birth")
            )
            contact_obj.save()
            contact_obj = contact_serializer.save()
            contact_obj.teams.clear()
            if data.get("teams"):
                teams_list = json.loads(data.get("teams"))
                teams = Teams.objects.filter(id__in=teams_list, org=request.profile.org)
                contact_obj.teams.add(*teams)

            contact_obj.assigned_to.clear()
            if data.get("assigned_to"):
                assinged_to_list = json.loads(data.get("assigned_to"))
                profiles = Profile.objects.filter(
                    id__in=assinged_to_list, org=request.profile.org
                )
                contact_obj.assigned_to.add(*profiles)

            previous_assigned_to_users = list(
                contact_obj.assigned_to.all().values_list("id", flat=True)
            )

            assigned_to_list = list(
                contact_obj.assigned_to.all().values_list("id", flat=True)
            )
            recipients = list(set(assigned_to_list) - set(previous_assigned_to_users))
            send_email_to_assigned_user.delay(
                recipients,
                contact_obj.id,
            )
            if request.FILES.get("contact_attachment"):
                attachment = Attachments()
                attachment.created_by = request.profile.user
                attachment.file_name = request.FILES.get("contact_attachment").name
                attachment.contact = contact_obj
                attachment.attachment = request.FILES.get("contact_attachment")
                attachment.save()
            return Response(
                {"error": False, "message": "Contact Updated Successfully", "contact": ContactSerializer(contact_obj).data},
                status=status.HTTP_200_OK,
            )

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params
    )
    def get(self, request, pk, format=None):
        context = {}
        contact_obj = self.get_object(pk, request.profile.org)
        context["contact_obj"] = ContactSerializer(contact_obj).data
        user_assgn_list = [
            assigned_to.id for assigned_to in contact_obj.assigned_to.all()
        ]
        user_assigned_accounts = set(
            self.request.profile.account_assigned_users.values_list("id", flat=True)
        )
        contact_accounts = set(
            contact_obj.account_contacts.values_list("id", flat=True)
        )
        if user_assigned_accounts.intersection(contact_accounts):
            user_assgn_list.append(self.request.profile.id)
        if self.request.profile.user == contact_obj.created_by:
            user_assgn_list.append(self.request.profile.id)
        if (self.request.profile.role not in [Constants.ADMIN, Constants.SALES_MANAGER] 
            and not self.request.profile.is_admin):
            if self.request.profile.id not in user_assgn_list:
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        assigned_data = []
        for each in contact_obj.assigned_to.all():
            assigned_dict = {}
            assigned_dict["id"] = each.user.id
            assigned_dict["name"] = each.user.email
            assigned_data.append(assigned_dict)

        if (self.request.profile.is_admin 
            or self.request.profile.role in [Constants.ADMIN, Constants.SALES_MANAGER]):
            users_mention = list(
                Profile.objects.filter(is_active=True, org=request.profile.org).values(
                    "user__email"
                )
            )
        elif self.request.profile.user != contact_obj.created_by:
            users_mention = [{"username": contact_obj.created_by.email}]
        else:
            users_mention = list(contact_obj.assigned_to.all().values("user__email"))

        if request.profile.user == contact_obj.created_by:
            user_assgn_list.append(self.request.profile.id)

        context["address_obj"] = BillingAddressSerializer(contact_obj.address).data
        context.update(
            {
                "comments": CommentSerializer(
                    contact_obj.contact_comments.all(), many=True
                ).data,
                "attachments": AttachmentsSerializer(
                    contact_obj.contact_attachment.all(), many=True
                ).data,
                "assigned_data": assigned_data,
                "tasks": TaskSerializer(
                    contact_obj.contacts_tasks.all(), many=True
                ).data,
                "users_mention": users_mention,
            }
        )
        return Response(context)

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        self.object = self.get_object(pk, org=request.profile.org)
        if self.object.org != request.profile.org:
            return Response(
                {"error": True, "errors": "User company doesnot match with header...."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if (
            self.request.profile.role not in [Constants.ADMIN, Constants.SALES_MANAGER]
            and not self.request.profile.is_admin
            and self.request.profile.user != self.object.created_by
        ):
            return Response(
                {
                    "error": True,
                    "errors": "You don't have permission to perform this action.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        self.object.delete()
        return Response(
            {"error": False, "message": "Contact Deleted Successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    # This commented-out method is kept here for later use.
    # @extend_schema(
    #     tags=["Contacts"], parameters=swagger_params1.organization_params,request=ContactDetailEditSwaggerSerializer
    # )
    # def post(self, request, pk, **kwargs):
    #     params = request.data
    #     context = {}
    #     self.contact_obj = Contact.objects.get(pk=pk)
    #     if self.request.profile.role != Constants.ADMIN and not self.request.profile.is_admin:
    #         if not (
    #             (self.request.profile.user == self.contact_obj.created_by)
    #             or (self.request.profile.user in self.contact_obj.assigned_to.all())
    #         ):
    #             return Response(
    #                 {
    #                     "error": True,
    #                     "errors": "You do not have Permission to perform this action",
    #                 },
    #                 status=status.HTTP_403_FORBIDDEN,
    #             )
    #     comment_serializer = CommentSerializer(data=params)
    #     if comment_serializer.is_valid():
    #         if params.get("comment"):
    #             comment_serializer.save(
    #                 contact_id=self.contact_obj.id,
    #                 commented_by_id=self.request.profile.id,
    #             )

    #     if self.request.FILES.get("contact_attachment"):
    #         attachment = Attachments()
    #         attachment.created_by = self.request.profile.user
    #         attachment.file_name = self.request.FILES.get("contact_attachment").name
    #         attachment.contact = self.contact_obj
    #         attachment.attachment = self.request.FILES.get("contact_attachment")
    #         attachment.save()

    #     comments = Comment.objects.filter(contact__id=self.contact_obj.id).order_by(
    #         "-id"
    #     )
    #     attachments = Attachments.objects.filter(
    #         contact__id=self.contact_obj.id
    #     ).order_by("-id")
    #     context.update(
    #         {
    #             "contact_obj": ContactSerializer(self.contact_obj).data,
    #             "attachments": AttachmentsSerializer(attachments, many=True).data,
    #             "comments": CommentSerializer(comments, many=True).data,
    #         }
    #     )
    #     return Response(context)


class ContactCommentView(APIView):
    model = Comment
    # #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)
    
    @extend_schema(tags=["Contacts"], parameters=swagger_params1.organization_params,request=ContactCommentEditSwaggerSerializer)
    def post(self, request, pk, **kwargs):
        params = request.data
        self.contact_obj = get_object_or_404(Contact, pk=pk, org=request.profile.org)
    
        if (
            self.request.profile.role not in [Constants.ADMIN, Constants.SALES_MANAGER] 
            and not self.request.user.is_superuser):
            if not (
                (self.request.profile.user == self.contact_obj.created_by)
                or (self.request.profile in self.contact_obj.assigned_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        comment_serializer = CommentSerializer(data=params)
        if comment_serializer.is_valid():
            if params.get("comment"):
                new_comment = comment_serializer.save(
                    commented_on= datetime.datetime.now(),
                    commented_by= self.request.profile,
                    contact=self.contact_obj,
                    # commented_by_id=self.request.profile.id,
                )
                return Response({"comment": ContactCommentSerializer(new_comment).data})
        else:
            return Response(
                {
                    "error": True,
                    "errors": "Invalid content",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params,request=ContactCommentEditSwaggerSerializer
    )
    def put(self, request, pk, format=None):
        params = request.data
        comment = self.get_object(pk)
        if (
            request.profile.role in [Constants.ADMIN, Constants.SALES_MANAGER]
            or request.profile.is_admin
            or request.profile == comment.commented_by
        ):
            serializer = CommentSerializer(comment, data=params)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"error": False, "message": "Comment Submitted"},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": True, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "error": True,
                "errors": "You don't have permission to edit this Comment",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        self.object = self.get_object(pk)
        if (
            request.profile.role in [Constants.ADMIN, Constants.SALES_MANAGER]
            or request.profile.is_admin
            or request.profile == self.object.commented_by
        ):
            self.object.delete()
            return Response(
                {"error": False, "message": "Comment Deleted Successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {
                "error": True,
                "errors": "You don't have permission to perform this action",
            },
            status=status.HTTP_403_FORBIDDEN,
        )


class ContactAttachmentView(APIView):
    model = Attachments
    # #authentication_classes = (CustomDualAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params
    )
    def delete(self, request, pk, format=None):
        self.object = get_object_or_404(self.model, pk=pk)
        if (
            request.profile.role in [Constants.ADMIN, Constants.SALES_MANAGER]
            or request.profile.is_admin
            or request.profile.user == self.object.created_by
        ):
            self.object.delete()
            return Response(
                {"error": False, "message": "Attachment Deleted Successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {
                "error": True,
                "errors": "You don't have permission to delete this Attachment",
            },
            status=status.HTTP_403_FORBIDDEN,
        )
    
    @extend_schema(
        tags=["Contacts"], parameters=swagger_params1.organization_params,request=ContactAttachmentSwaggerSerializer
    )
    def post(self, request, pk, **kwargs):
        params = request.data
        context = {}
        self.contact_obj = get_object_or_404(Contact, pk=pk, org=request.profile.org)
        if (self.request.profile.role not in [Constants.ADMIN, Constants.SALES_MANAGER] 
            and not self.request.profile.is_admin):
            if not (
                (self.request.profile.user == self.contact_obj.created_by)
                or (self.request.profile.user in self.contact_obj.assigned_to.all())
            ):
                return Response(
                    {
                        "error": True,
                        "errors": "You do not have Permission to perform this action",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        comment_serializer = CommentSerializer(data=params)
        if comment_serializer.is_valid():
            if params.get("comment"):
                comment_serializer.save(
                    contact_id=self.contact_obj.id,
                    commented_by_id=self.request.profile.id,
                )

        if self.request.FILES.get("contact_attachment"):
            attachment = Attachments()
            attachment.created_by = self.request.profile.user
            attachment.file_name = self.request.FILES.get("contact_attachment").name
            attachment.contact = self.contact_obj
            attachment.attachment = self.request.FILES.get("contact_attachment")
            attachment.save()

        comments = Comment.objects.filter(contact__id=self.contact_obj.id).order_by(
            "-id"
        )
        attachments = Attachments.objects.filter(
            contact__id=self.contact_obj.id
        ).order_by("-id")
        context.update(
            {
                "contact_obj": ContactSerializer(self.contact_obj).data,
                "attachments": AttachmentsSerializer(attachments, many=True).data,
                "comments": CommentSerializer(comments, many=True).data,
            }
        )
        return Response(context)
