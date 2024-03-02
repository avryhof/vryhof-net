from django.conf import settings
from rest_framework import permissions

from accounts.session_helpers import get_oauth_session


class AuthorizedAgentPermission(permissions.BasePermission):
    """
    Check if the request has a valid agent string at minimum
    """

    def has_permission(self, request, view):
        is_authorized = False
        allowed_agents = getattr(settings, 'ALLOWED_API_AGENTS', '')

        agent = request.headers.get("KPH-Agent")

        if agent in allowed_agents:
            is_authorized = True

        return is_authorized


class LoggedInPermission(permissions.BasePermission):
    """Check if user is logged in"""

    def has_permission(self, request, view):
        oauth_session = get_oauth_session(request, active=True)
        if oauth_session is not None:
            user = oauth_session.user
        else:
            user = request.user

        if not user or not user.is_active:
            return False

        else:
            return True
