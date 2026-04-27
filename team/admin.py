from django.contrib import admin

from .models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "role", "email", "is_active", "order")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    search_fields = ("first_name", "last_name", "role", "bio")
    ordering = ("order", "last_name")
