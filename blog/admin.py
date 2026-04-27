from django.contrib import admin

from .models import Category, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "author", "published_at")
    list_filter = ("status", "category")
    list_select_related = ("category", "author")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary", "body")
