from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ApiRootView,
    AppointmentRequestDetailAPIView,
    AppointmentEmailVerifyAPIView,
    AppointmentRequestListCreateAPIView,
    CategoryListAPIView,
    ContactSubmissionListCreateAPIView,
    DashboardUserListAPIView,
    CurrentUserAPIView,
    HomePageAPIView,
    PostDetailAPIView,
    PostListAPIView,
    RegisterUserAPIView,
    ServiceDetailAPIView,
    ServiceListAPIView,
    TeamMemberDetailAPIView,
    TeamMemberListAPIView,
)

app_name = "api"

urlpatterns = [
    path("", ApiRootView.as_view(), name="root"),
    path("auth/register/", RegisterUserAPIView.as_view(), name="register-user"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", CurrentUserAPIView.as_view(), name="current-user"),
    path("users/", DashboardUserListAPIView.as_view(), name="user-list"),
    path("home/", HomePageAPIView.as_view(), name="home"),
    path("services/", ServiceListAPIView.as_view(), name="service-list"),
    path("services/<slug:slug>/", ServiceDetailAPIView.as_view(), name="service-detail"),
    path("team/", TeamMemberListAPIView.as_view(), name="team-list"),
    path("team/<slug:slug>/", TeamMemberDetailAPIView.as_view(), name="team-detail"),
    path("blog/categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("blog/posts/", PostListAPIView.as_view(), name="post-list"),
    path("blog/posts/<slug:slug>/", PostDetailAPIView.as_view(), name="post-detail"),
    path("contact-submissions/", ContactSubmissionListCreateAPIView.as_view(), name="contact-list-create"),
    path("contact-submissions/", ContactSubmissionListCreateAPIView.as_view(), name="contact-create"),
    path("appointments/", AppointmentRequestListCreateAPIView.as_view(), name="appointment-list-create"),
    path("appointments/", AppointmentRequestListCreateAPIView.as_view(), name="appointment-create"),
    path("appointments/verify-email/<path:token>/", AppointmentEmailVerifyAPIView.as_view(), name="appointment-verify-email"),
    path("appointments/<int:pk>/", AppointmentRequestDetailAPIView.as_view(), name="appointment-detail"),
]
