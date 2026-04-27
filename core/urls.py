from django.urls import path

from .views import about, home

app_name = "core"

urlpatterns = [
    path("", home, name="home"),
    path("about/", about, name="about"),
]
