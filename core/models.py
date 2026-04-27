from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=150, default="Cabinet Nyamugabo")
    tagline = models.CharField(max_length=255, blank=True)
    hero_title = models.CharField(max_length=200)
    hero_subtitle = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    office_address = models.TextField(blank=True)
    cta_label = models.CharField(max_length=100, blank=True)
    cta_link = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "site setting"
        verbose_name_plural = "site settings"

    def __str__(self):
        return self.site_name


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "question"]

    def __str__(self):
        return self.question
