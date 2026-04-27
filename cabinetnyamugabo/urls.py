from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("api/", include("api.urls")),
    path("services/", include("services.urls")),
    path("team/", include("team.urls")),
    path("blog/", include("blog.urls")),
    path("contact/", include("contact.urls")),
    path("appointments/", include("appointment.urls")),
    path("admin/", admin.site.urls),
]
