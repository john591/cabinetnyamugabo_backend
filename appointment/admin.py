from django.contrib import admin

from .models import AppointmentRequest


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "country", "office", "service", "preferred_date", "status")
    list_filter = ("country", "office", "status", "preferred_date")
    list_select_related = ("service",)
    search_fields = ("name", "email", "phone", "country", "office", "message")
    readonly_fields = ("created_at",)
