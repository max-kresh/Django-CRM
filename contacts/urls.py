from django.urls import path

from contacts import views

app_name = "api_contacts"

urlpatterns = [
    path("", views.ContactsListView.as_view(), name="contacts-list"),
    path("<uuid:pk>/", views.ContactDetailView.as_view()),
    path("comment/<uuid:pk>/", views.ContactCommentView.as_view()),
    path("attachment/<uuid:pk>/", views.ContactAttachmentView.as_view()),
]
 