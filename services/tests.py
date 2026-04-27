from django.test import TestCase
from django.urls import reverse

from .models import Service


class ServiceModelTests(TestCase):
    def test_slug_is_generated(self):
        service = Service.objects.create(
            title="Tax Advisory",
            short_description="Tax support.",
            description="Detailed service description.",
        )
        self.assertEqual(service.slug, "tax-advisory")
        self.assertEqual(str(service), "Tax Advisory")


class ServiceViewTests(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            title="Employment Law",
            short_description="Employment support.",
            description="Employment disputes and compliance.",
        )

    def test_service_list_page(self):
        response = self.client.get(reverse("services:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.title)

    def test_service_detail_page(self):
        response = self.client.get(self.service.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service.description)
