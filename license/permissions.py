from rest_framework import permissions
from django.conf import settings
from .utils import verify_api_token


class HasAPIToken(permissions.BasePermission):
    """
    Custom permission to check for a dynamic time-based API Token.
    Valid for current and previous hour.
    """
    def has_permission(self, request, view):
        # Get token from header or query parameter
        token = request.headers.get('X-API-TOKEN') or request.query_params.get('token')

        if not settings.API_TOKEN:
            return False

        return verify_api_token(token, settings.API_TOKEN)


class HasStaticAPIKey(permissions.BasePermission):
    """
    Static API Key authentication for production use.
    Checks for API key from header or query parameter.

    Usage in .env:
    API_TOKEN=your-strong-random-secret-key-here

    Client usage:
    - Header: X-API-TOKEN: your-key
    - Query: ?token=your-key
    """
    def has_permission(self, request, view):
        # Get token from header or query parameter
        api_key = request.headers.get('X-API-TOKEN') or request.query_params.get('token')

        if not api_key:
            return False

        if not settings.API_TOKEN:
            return False

        # Simple string comparison for static key
        return api_key == settings.API_TOKEN
