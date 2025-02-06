from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from common import views

app_name = "api_common"


urlpatterns = [
    path("dashboard/", views.ApiHomeView.as_view()),
    path(
        "auth/refresh-token/",
        jwt_views.TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    # GoogleLoginView
    path("auth/google/", views.GoogleLoginView.as_view()),
    path("auth/email/", views.UserLoginView.as_view(), name="user-login"),
    path("auth/activate-user/", views.CreatePasswordView.as_view(), name="create-password"),
    path("org/", views.OrgProfileCreateView.as_view(), name="org-profile"),
    path("profile/", views.ProfileView.as_view()),
    path("users/get-teams-and-users/", views.GetTeamsAndUsersView.as_view()),
    path("users/", views.UsersListView.as_view(), name="users-list"),
    path("user/<str:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("documents/", views.DocumentListView.as_view()),
    path("documents/<str:pk>/", views.DocumentDetailView.as_view()),
    path("api-settings/", views.DomainList.as_view()),
    path("api-settings/<str:pk>/", views.DomainDetailView.as_view()),
    path("user/<str:pk>/status/", views.UserStatusView.as_view()),
    path("app-settings/", view=views.AppSettingsView.as_view(), name="app-settings")
]
