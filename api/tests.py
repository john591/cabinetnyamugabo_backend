from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from appointment.models import AppointmentRequest
from blog.models import Category, Post
from services.models import Service
from team.models import TeamMember


class ApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="admin",
            password="strong-pass-123",
            email="admin@example.com",
            is_staff=True,
        )
        self.service = Service.objects.create(
            title="Commercial Law",
            short_description="Commercial legal support.",
            description="Full service commercial legal support.",
            is_featured=True,
        )
        self.member = TeamMember.objects.create(
            first_name="Nadia",
            last_name="Mukendi",
            role="Partner",
            bio="Advises on corporate and commercial matters.",
        )
        self.category = Category.objects.create(name="Insights")
        self.post = Post.objects.create(
            title="Cross-Border Advisory",
            summary="A summary for the frontend.",
            body="A detailed article body for the frontend.",
            category=self.category,
            author=self.member,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_api_root_lists_endpoints(self):
        response = self.client.get(reverse("api:root"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("services", response.json())
        self.assertIn("register", response.json())

    def test_home_api_returns_featured_content(self):
        response = self.client.get(reverse("api:home"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["featured_services"][0]["slug"], self.service.slug)
        self.assertEqual(payload["team_members"][0]["slug"], self.member.slug)
        self.assertEqual(payload["latest_posts"][0]["slug"], self.post.slug)

    def test_service_detail_api(self):
        response = self.client.get(reverse("api:service-detail", args=[self.service.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], self.service.title)

    def test_service_create_api(self):
        response = self.client.post(
            reverse("api:service-list"),
            data={
                "title": "Tax Advisory",
                "short_description": "Tax planning and disputes.",
                "description": "Support across tax compliance and litigation.",
                "is_featured": False,
                "order": 3,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        login = self.client.post(
            reverse("api:token-obtain-pair"),
            data={"username": "admin", "password": "strong-pass-123"},
            content_type="application/json",
        )
        token = login.json()["access"]
        response = self.client.post(
            reverse("api:service-list"),
            data={
                "title": "Tax Advisory",
                "short_description": "Tax planning and disputes.",
                "description": "Support across tax compliance and litigation.",
                "is_featured": False,
                "order": 3,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["slug"], "tax-advisory")

    def test_team_member_create_api(self):
        response = self.client.post(
            reverse("api:team-list"),
            data={
                "first_name": "Sarah",
                "last_name": "Ilunga",
                "role": "Associate",
                "bio": "Supports clients across compliance matters.",
                "email": "sarah@example.com",
                "is_active": True,
                "order": 2,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        login = self.client.post(
            reverse("api:token-obtain-pair"),
            data={"username": "admin", "password": "strong-pass-123"},
            content_type="application/json",
        )
        token = login.json()["access"]
        response = self.client.post(
            reverse("api:team-list"),
            data={
                "first_name": "Sarah",
                "last_name": "Ilunga",
                "role": "Associate",
                "bio": "Supports clients across compliance matters.",
                "email": "sarah@example.com",
                "is_active": True,
                "order": 2,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["slug"], "sarah-ilunga")

    def test_category_create_api(self):
        response = self.client.post(
            reverse("api:category-list"),
            data={
                "name": "Case Notes",
                "description": "Updates from recent matters.",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        login = self.client.post(
            reverse("api:token-obtain-pair"),
            data={"username": "admin", "password": "strong-pass-123"},
            content_type="application/json",
        )
        token = login.json()["access"]
        response = self.client.post(
            reverse("api:category-list"),
            data={
                "name": "Case Notes",
                "description": "Updates from recent matters.",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["slug"], "case-notes")

    def test_post_list_api_only_returns_published_posts(self):
        Post.objects.create(
            title="Draft Post",
            summary="Draft summary",
            body="Draft body",
            category=self.category,
            author=self.member,
            status=Post.Status.DRAFT,
        )
        response = self.client.get(reverse("api:post-list"))
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["slug"], self.post.slug)

    def test_post_create_api(self):
        response = self.client.post(
            reverse("api:post-list"),
            data={
                "title": "Regulatory Update",
                "summary": "A short frontend summary.",
                "body": "A full article for the frontend.",
                "category_id": self.category.pk,
                "author_id": self.member.pk,
                "status": "published",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        login = self.client.post(
            reverse("api:token-obtain-pair"),
            data={"username": "admin", "password": "strong-pass-123"},
            content_type="application/json",
        )
        token = login.json()["access"]
        response = self.client.post(
            reverse("api:post-list"),
            data={
                "title": "Regulatory Update",
                "summary": "A short frontend summary.",
                "body": "A full article for the frontend.",
                "category_id": self.category.pk,
                "author_id": self.member.pk,
                "status": "published",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Regulatory Update")
        self.assertEqual(response.json()["category"]["slug"], self.category.slug)

    def test_post_update_api(self):
        response = self.client.patch(
            reverse("api:post-detail", args=[self.post.slug]),
            data={
                "summary": "Updated summary for React.",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        login = self.client.post(
            reverse("api:token-obtain-pair"),
            data={"username": "admin", "password": "strong-pass-123"},
            content_type="application/json",
        )
        token = login.json()["access"]
        response = self.client.patch(
            reverse("api:post-detail", args=[self.post.slug]),
            data={
                "summary": "Updated summary for React.",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["summary"], "Updated summary for React.")

    def test_jwt_login_and_me_api(self):
        login = self.client.post(
            reverse("api:token-obtain-pair"),
            data={"username": "admin", "password": "strong-pass-123"},
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access"]

        me = self.client.get(
            reverse("api:current-user"),
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["username"], "admin")

    def test_register_user_api_creates_user_and_returns_tokens(self):
        response = self.client.post(
            reverse("api:register-user"),
            data={
                "username": "editor",
                "email": "editor@example.com",
                "first_name": "Edit",
                "last_name": "Or",
                "password": "another-strong-pass",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["username"], "editor")
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_register_user_api_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("api:register-user"),
            data={
                "username": "other-admin",
                "email": "admin@example.com",
                "password": "another-strong-pass",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CONTACT_NOTIFICATION_EMAILS=["admin@example.com"],
    )
    def test_contact_submission_api_creates_record_and_sends_email(self):
        response = self.client.post(
            reverse("api:contact-create"),
            data={
                "name": "Frontend Client",
                "email": "frontend@example.com",
                "phone": "+243900000000",
                "subject": "Need legal support",
                "message": "Please contact me.",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "new")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Need legal support", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["admin@example.com"])

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        APPOINTMENT_NOTIFICATION_EMAILS=["appointments@example.com"],
        APPOINTMENT_CONFIRMATION_SUBJECT="We received your appointment request",
        APPOINTMENT_EMAIL_VERIFICATION_SUBJECT="Verify your email",
        FRONTEND_BASE_URL="",
    )
    @patch("appointment.verification.send_appointment_request_sms_confirmation")
    def test_appointment_api_verifies_email_before_saving(self, send_sms_confirmation):
        response = self.client.post(
            reverse("api:appointment-create"),
            data={
                "name": "Frontend Client",
                "email": "frontend@example.com",
                "phone": "+243911111111",
                "country": AppointmentRequest.Country.DRC,
                "office": AppointmentRequest.Office.KINSHASA,
                "service_id": self.service.pk,
                "preferred_date": str(timezone.localdate() + timedelta(days=3)),
                "preferred_time": "11:00:00",
                "message": "I need an appointment.",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(AppointmentRequest.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Verify your email")
        self.assertEqual(mail.outbox[0].to, ["frontend@example.com"])
        send_sms_confirmation.assert_not_called()

        verify_url = next(
            line for line in mail.outbox[0].body.splitlines() if "/appointments/verify-email/" in line
        )
        verify_path = verify_url.split("testserver", 1)[1]
        response = self.client.get(verify_path)

        self.assertRedirects(response, reverse("appointment:success"))
        self.assertEqual(AppointmentRequest.objects.count(), 1)
        self.assertEqual(AppointmentRequest.objects.get().country, AppointmentRequest.Country.DRC)
        self.assertEqual(AppointmentRequest.objects.get().office, AppointmentRequest.Office.KINSHASA)
        self.assertEqual(len(mail.outbox), 3)
        self.assertIn("New appointment request", mail.outbox[1].subject)
        self.assertEqual(mail.outbox[1].to, ["appointments@example.com"])
        self.assertEqual(mail.outbox[2].subject, "We received your appointment request")
        self.assertEqual(mail.outbox[2].to, ["frontend@example.com"])
        send_sms_confirmation.assert_called_once()

    def test_appointment_api_rejects_past_date(self):
        response = self.client.post(
            reverse("api:appointment-create"),
            data={
                "name": "Frontend Client",
                "email": "frontend@example.com",
                "preferred_date": str(timezone.localdate() - timedelta(days=1)),
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("preferred_date", response.json())
