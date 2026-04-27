from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role_title", "phone", "is_dashboard_user", "updated_at")
    list_filter = ("is_dashboard_user",)
    search_fields = ("user__username", "user__email", "role_title", "phone")
