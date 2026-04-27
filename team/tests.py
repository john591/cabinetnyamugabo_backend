from django.test import TestCase
from django.urls import reverse

from .models import TeamMember


class TeamMemberModelTests(TestCase):
    def test_full_name_and_slug(self):
        member = TeamMember.objects.create(
            first_name="Grace",
            last_name="Ilunga",
            role="Associate",
            bio="Handles client advisory work.",
        )
        self.assertEqual(member.full_name, "Grace Ilunga")
        self.assertEqual(member.slug, "grace-ilunga")


class TeamViewTests(TestCase):
    def setUp(self):
        self.member = TeamMember.objects.create(
            first_name="Grace",
            last_name="Ilunga",
            role="Associate",
            bio="Handles client advisory work.",
        )

    def test_team_list_page(self):
        response = self.client.get(reverse("team:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.full_name)

    def test_team_detail_page(self):
        response = self.client.get(self.member.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.member.bio)
