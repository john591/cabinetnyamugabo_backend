from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import UserProfile


class AccountModelTests(TestCase):
    def test_profile_is_created_for_new_user(self):
        user = get_user_model().objects.create_user(
            username="dashboarduser",
            email="dashboard@example.com",
            password="strong-pass-123",
        )
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(str(user.profile), "Profile for dashboarduser")
