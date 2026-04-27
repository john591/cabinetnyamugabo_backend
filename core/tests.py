from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from blog.models import Category, Post
from core.models import FAQ, SiteSetting
from services.models import Service
from team.models import TeamMember


class CoreModelTests(TestCase):
    def test_site_setting_string_representation(self):
        setting = SiteSetting.objects.create(
            site_name="Cabinet Nyamugabo",
            hero_title="Trusted legal support",
        )
        self.assertEqual(str(setting), "Cabinet Nyamugabo")

    def test_faq_ordering(self):
        FAQ.objects.create(question="Second question?", answer="Answer", order=2)
        first = FAQ.objects.create(question="First question?", answer="Answer", order=1)
        self.assertEqual(FAQ.objects.first(), first)


class CoreViewTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Corporate Law",
            short_description="Business legal services.",
            description="Corporate legal support.",
            is_featured=True,
        )
        self.member = TeamMember.objects.create(
            first_name="Aline",
            last_name="Kasongo",
            role="Counsel",
            bio="Experienced legal adviser.",
        )
        category = Category.objects.create(name="Insights")
        Post.objects.create(
            title="Published Post",
            summary="Useful legal update.",
            body="Body",
            category=category,
            author=self.member,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_home_page_renders(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.title)
        self.assertContains(response, self.member.full_name)

    def test_about_page_renders(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.role)
