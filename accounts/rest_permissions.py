from django.conf import settings
from rest_framework import permissions

from accounts.lib_utils import load_model


class AuthorizedAgentPermission(permissions.BasePermission):
    """
    Check if the request has a valid agent string at minimum
    """

    def has_permission(self, request, view):
        is_authorized = False
        allowed_agents = getattr(settings, "ALLOWED_API_AGENTS", "")

        agent = request.headers.get("KPH-Agent")

        if agent in allowed_agents:
            is_authorized = True

        return is_authorized


class LoggedInPermission(permissions.BasePermission):
    """Check if user is logged in"""

    def has_permission(self, request, view):
        session_model = load_model("accounts.AuthSession")

        try:
            auth_session = session_model.objects.get(user=request.user)
        except session_model.DoesNotExist:
            return False
        else:
            return auth_session.is_authenticated
