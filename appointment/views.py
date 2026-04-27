from django.core import signing
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, View

from .forms import AppointmentRequestForm
from .models import AppointmentRequest
from .verification import (
    appointment_payload_from_data,
    create_verified_appointment,
    load_appointment_verification_payload,
    send_appointment_email_verification,
)


class AppointmentRequestCreateView(CreateView):
    model = AppointmentRequest
    form_class = AppointmentRequestForm
    template_name = "appointment/appointment_form.html"
    success_url = reverse_lazy("appointment:verification-sent")

    def form_valid(self, form):
        payload = appointment_payload_from_data(form.cleaned_data)
        send_appointment_email_verification(self.request, payload)
        return redirect(self.success_url)


class AppointmentVerificationSentView(TemplateView):
    template_name = "appointment/appointment_verification_sent.html"


class AppointmentVerifyEmailView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            payload = load_appointment_verification_payload(token)
        except signing.BadSignature:
            return redirect("appointment:verification-invalid")

        create_verified_appointment(payload)
        return redirect("appointment:success")


class AppointmentVerificationInvalidView(TemplateView):
    template_name = "appointment/appointment_verification_invalid.html"


class AppointmentSuccessView(TemplateView):
    template_name = "appointment/appointment_success.html"
