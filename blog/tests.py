from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from team.models import TeamMember

from .models import Category, Post


class BlogModelTests(TestCase):
    def setUp(self):
        self.author = TeamMember.objects.create(
            first_name="Joel",
            last_name="Mwamba",
            role="Partner",
            bio="Writes on legal strategy.",
        )
        self.category = Category.objects.create(name="News")

    def test_published_post_sets_publication_date(self):
        post = Post.objects.create(
            title="A Timely Update",
            summary="Summary",
            body="Body",
            category=self.category,
            author=self.author,
            status=Post.Status.PUBLISHED,
        )
        self.assertIsNotNone(post.published_at)
        self.assertEqual(post.slug, "a-timely-update")

    def test_only_published_posts_are_returned(self):
        Post.objects.create(
            title="Draft",
            summary="Draft summary",
            body="Draft body",
            category=self.category,
            author=self.author,
            status=Post.Status.DRAFT,
        )
        published = Post.objects.create(
            title="Published",
            summary="Published summary",
            body="Published body",
            category=self.category,
            author=self.author,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )
        self.assertEqual(list(Post.objects.published()), [published])


class BlogViewTests(TestCase):
    def setUp(self):
        author = TeamMember.objects.create(
            first_name="Joel",
            last_name="Mwamba",
            role="Partner",
            bio="Writes on legal strategy.",
        )
        category = Category.objects.create(name="News")
        self.post = Post.objects.create(
            title="Compliance Outlook",
            summary="Summary",
            body="Body copy",
            category=category,
            author=author,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_post_list_page(self):
        response = self.client.get(reverse("blog:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.title)

    def test_post_detail_page(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.post.summary)
