from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from appointment.models import AppointmentRequest
from blog.models import Category, Post
from contact.models import ContactSubmission
from services.models import Service
from team.models import TeamMember


class Command(BaseCommand):
    help = "Seed sample data for local development."

    def handle(self, *args, **options):
        litigation = Service.objects.get_or_create(
            slug="litigation",
            defaults={
                "title": "Litigation",
                "short_description": "Representation in civil and commercial disputes.",
                "description": "We support clients through disputes, negotiations, and courtroom proceedings.",
                "icon": "scale-balanced",
                "is_featured": True,
                "order": 1,
            },
        )[0]
        advisory = Service.objects.get_or_create(
            slug="business-advisory",
            defaults={
                "title": "Business Advisory",
                "short_description": "Practical legal guidance for growing businesses.",
                "description": "We advise founders and companies on compliance, contracts, and operations.",
                "icon": "briefcase",
                "is_featured": True,
                "order": 2,
            },
        )[0]

        lead_member = TeamMember.objects.get_or_create(
            slug="nyamugabo-kalume",
            defaults={
                "first_name": "Nyamugabo",
                "last_name": "Kalume",
                "role": "Managing Counsel",
                "bio": "Leads client strategy across dispute resolution and advisory work.",
                "email": "contact@example.com",
                "is_active": True,
                "order": 1,
            },
        )[0]

        insights = Category.objects.get_or_create(
            slug="insights",
            defaults={
                "name": "Insights",
                "description": "Updates on legal developments and firm perspectives.",
            },
        )[0]

        Post.objects.get_or_create(
            slug="welcome-to-our-firm-journal",
            defaults={
                "title": "Welcome to Our Firm Journal",
                "summary": "A new space for legal insights, case notes, and practical guidance.",
                "body": "This journal shares timely updates, practical commentary, and firm news.",
                "category": insights,
                "author": lead_member,
                "status": Post.Status.PUBLISHED,
                "published_at": timezone.now(),
            },
        )

        ContactSubmission.objects.get_or_create(
            email="prospect@example.com",
            subject="Consultation request",
            defaults={
                "name": "Prospective Client",
                "phone": "+243900000000",
                "message": "I would like to discuss a business advisory matter.",
            },
        )

        AppointmentRequest.objects.get_or_create(
            email="appointment@example.com",
            preferred_date=timezone.localdate() + timedelta(days=7),
            defaults={
                "name": "Meeting Request",
                "phone": "+243911111111",
                "country": AppointmentRequest.Country.DRC,
                "office": AppointmentRequest.Office.KINSHASA,
                "service": advisory,
                "preferred_time": time(10, 0),
                "message": "Please confirm availability for an initial consultation.",
            },
        )

        self.stdout.write(self.style.SUCCESS("Sample site data created or already present."))
