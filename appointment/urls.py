from django.urls import path

from .views import (
    AppointmentRequestCreateView,
    AppointmentSuccessView,
    AppointmentVerificationInvalidView,
    AppointmentVerificationSentView,
    AppointmentVerifyEmailView,
)

app_name = "appointment"

urlpatterns = [
    path("", AppointmentRequestCreateView.as_view(), name="create"),
    path("verification-sent/", AppointmentVerificationSentView.as_view(), name="verification-sent"),
    path("verify-email/<path:token>/", AppointmentVerifyEmailView.as_view(), name="verify-email"),
    path(
        "verification-invalid/",
        AppointmentVerificationInvalidView.as_view(),
        name="verification-invalid",
    ),
    path("success/", AppointmentSuccessView.as_view(), name="success"),
]
