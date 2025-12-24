"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from license.views import login_view, logout_view, index_view


@csrf_exempt
def health_check(request):
    """Health check endpoint for monitoring"""
    _ = request  # Acknowledge request parameter
    return JsonResponse({
        'status': 'healthy',
        'environment': 'development' if settings.DEBUG else 'production'
    })


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view - requires login"""
    template_name = "dashboard.html"
    login_url = '/login/'


urlpatterns = [
    path("", index_view, name="index"),
    path("health/", health_check, name="health_check"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("admin/", admin.site.urls),
    path("api/", include("license.urls")),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
