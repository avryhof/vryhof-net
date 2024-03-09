from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication

from accounts.lib_utils import load_model, log_message


class CsrfExemptSessionAuthentication(authentication.SessionAuthentication):

    def enforce_csrf(self, request):
        return

    def authenticate(self, request):
        http_request = request._request
        user = getattr(http_request, "user", None)

        if not user or not user.is_active:
            return None

        return (user, None)


class RemoteSessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        session_model = load_model("accounts.AuthSession")

        auth = None
        user = AnonymousUser()

        auth_token = None
        try:
            auth_token = request.data.get("auth_token")
        except Exception as e:
            log_message(message=f"No token supplied {dict(request.data)}")

        try:
            remote = session_model.objects.get(token=auth_token)
        except session_model.DoesNotExist:
            pass
        else:
            user = remote.user

        return (user, auth)
