from django.contrib import admin

from .models import FAQ, SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "contact_phone", "updated_at")
    search_fields = ("site_name", "tagline", "contact_email", "contact_phone")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("question", "answer")
    ordering = ("order", "question")
