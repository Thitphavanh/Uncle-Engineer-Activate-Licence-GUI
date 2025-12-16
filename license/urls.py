from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SoftwareNameViewSet, LicenseViewSet, ActivationLogViewSet

# สร้าง Router
router = DefaultRouter()
router.register(r"software", SoftwareNameViewSet, basename="software")
router.register(r"licenses", LicenseViewSet, basename="license")
router.register(r"logs", ActivationLogViewSet, basename="log")

urlpatterns = [
    path("", include(router.urls)),
]
