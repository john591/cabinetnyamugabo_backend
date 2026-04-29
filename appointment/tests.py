from datetime import timedelta
from urllib.parse import urlparse
from unittest.mock import patch

from django.core import mail
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from services.models import Service

from .forms import AppointmentRequestForm
from .models import AppointmentRequest


class AppointmentFormTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Commercial Advisory",
            short_description="Support for businesses.",
            description="Detailed service.",
        )

    def test_appointment_form_rejects_past_date(self):
        form = AppointmentRequestForm(
            data={
                "name": "Client",
                "email": "client@example.com",
                "phone": "+243911111111",
                "country": AppointmentRequest.Country.DRC,
                "office": AppointmentRequest.Office.KINSHASA,
                "service": self.service.pk,
                "preferred_date": timezone.localdate() - timedelta(days=1),
                "preferred_time": "10:00",
                "message": "Need advice.",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("preferred_date", form.errors)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        APPOINTMENT_NOTIFICATION_EMAILS=["appointments@example.com"],
        APPOINTMENT_CONFIRMATION_SUBJECT="We received your appointment request",
        APPOINTMENT_EMAIL_VERIFICATION_SUBJECT="Verify your email",
        FRONTEND_BASE_URL="",
    )
    @patch("appointment.verification.send_appointment_request_sms_confirmation")
    def test_appointment_submission_verifies_email_before_saving(
        self, send_sms_confirmation
    ):
        response = self.client.post(
            reverse("appointment:create"),
            data={
                "name": "Client",
                "email": "client@example.com",
                "phone": "+243911111111",
                "country": AppointmentRequest.Country.DRC,
                "office": AppointmentRequest.Office.KINSHASA,
                "service": self.service.pk,
                "preferred_date": timezone.localdate() + timedelta(days=2),
                "preferred_time": "10:00",
                "message": "Need advice.",
            },
        )
        self.assertRedirects(response, reverse("appointment:verification-sent"))
        self.assertEqual(AppointmentRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Verify your email")
        self.assertEqual(mail.outbox[0].to, ["client@example.com"])
        self.assertIn("Cliquer ici pour verifier", mail.outbox[0].alternatives[0][0])
        send_sms_confirmation.assert_not_called()

        verify_url = next(
            line for line in mail.outbox[0].body.splitlines() if "/appointments/verify-email/" in line
        )
        verify_path = urlparse(verify_url).path
        response = self.client.get(verify_path)

        self.assertRedirects(response, reverse("appointment:success"))
        self.assertEqual(AppointmentRequest.objects.count(), 1)
        self.assertEqual(AppointmentRequest.objects.get().country, AppointmentRequest.Country.DRC)
        self.assertEqual(AppointmentRequest.objects.get().office, AppointmentRequest.Office.KINSHASA)
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(mail.outbox[1].to, ["appointments@example.com"])
        self.assertEqual(mail.outbox[2].to, ["client@example.com"])
        self.assertEqual(mail.outbox[2].subject, "We received your appointment request")
        self.assertIn("Votre demande de rendez-vous est recue", mail.outbox[2].alternatives[0][0])
        send_sms_confirmation.assert_called_once()

    @override_settings(
        DEBUG=True,
        DEFAULT_FRONTEND_BASE_URL="https://cabinenyamugabo.vercel.app",
        FRONTEND_BASE_URL="http://127.0.0.1:3000",
    )
    def test_public_frontend_url_does_not_use_localhost_even_when_debug_is_true(self):
        from .verification import get_public_frontend_base_url

        self.assertEqual(get_public_frontend_base_url(), "https://cabinenyamugabo.vercel.app")

    def test_appointment_form_renders_choice_selects(self):
        form = AppointmentRequestForm()
        self.assertEqual(form.fields["country"].widget.__class__.__name__, "Select")
        self.assertEqual(form.fields["office"].widget.__class__.__name__, "Select")
        self.assertIn(
            (AppointmentRequest.Country.DRC, "Democratic Republic of the Congo"),
            form.fields["country"].choices,
        )
        self.assertIn(
            (AppointmentRequest.Office.BUKAVU, "Bukavu"),
            form.fields["office"].choices,
        )

    def test_appointment_string_representation(self):
        appointment = AppointmentRequest.objects.create(
            name="Client",
            email="client@example.com",
            country=AppointmentRequest.Country.DRC,
            office=AppointmentRequest.Office.KINSHASA,
            service=self.service,
            preferred_date=timezone.localdate() + timedelta(days=1),
        )
        self.assertIn("Client", str(appointment))
