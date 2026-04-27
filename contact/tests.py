from django.test import TestCase
from django.urls import reverse

from .forms import ContactSubmissionForm
from .models import ContactSubmission


class ContactFormTests(TestCase):
    def test_contact_form_is_valid_with_required_fields(self):
        form = ContactSubmissionForm(
            data={
                "name": "Client",
                "email": "client@example.com",
                "phone": "+243900000000",
                "subject": "General inquiry",
                "message": "Please contact me.",
            }
        )
        self.assertTrue(form.is_valid())

    def test_contact_submission_route_creates_record(self):
        response = self.client.post(
            reverse("contact:create"),
            data={
                "name": "Client",
                "email": "client@example.com",
                "phone": "+243900000000",
                "subject": "General inquiry",
                "message": "Please contact me.",
            },
        )
        self.assertRedirects(response, reverse("contact:success"))
        self.assertEqual(ContactSubmission.objects.count(), 1)

    def test_contact_submission_string_representation(self):
        submission = ContactSubmission.objects.create(
            name="Client",
            email="client@example.com",
            subject="General inquiry",
            message="Please contact me.",
        )
        self.assertEqual(str(submission), "Client - General inquiry")
