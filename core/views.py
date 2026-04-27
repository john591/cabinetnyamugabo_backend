from django.shortcuts import render

from blog.models import Post
from services.models import Service
from team.models import TeamMember


def home(request):
    context = {
        "featured_services": Service.objects.filter(is_featured=True)[:3],
        "team_members": TeamMember.objects.filter(is_active=True)[:3],
        "latest_posts": Post.objects.published()[:3],
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "team_members": TeamMember.objects.filter(is_active=True),
    }
    return render(request, "core/about.html", context)
