"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path


def spa_index(request):
    """Serve the built SPA's index.html for any non-API route (history fallback).

    Client-side routes like /match/1/score are not real files, so WhiteNoise 404s
    and Django falls through to here. Absent build (local dev) -> 404, which is fine.
    """
    index = settings.FRONTEND_DIR / "index.html"
    if not index.exists():
        raise Http404("Frontend build not found. Run the Vite build or use the dev server.")
    return FileResponse(open(index, "rb"))


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("matches.urls")),
    # Catch-all: everything except api/, admin/, static/ serves the SPA shell.
    re_path(r"^(?!api/|admin/|static/).*$", spa_index),
]
