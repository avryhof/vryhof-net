import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from accounts.lib_utils import log_message, load_model, aware_now

logger = logging.getLogger(__name__)
ldap_print_debug = True


class AuthTokenBackend(ModelBackend):
    user_model = None

    def __init__(self):
        self.user_model = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        if username:
            auth_session_model = load_model("accounts.AuthSession")

            try:
                auth_user = self.user_model.objects.get(username=username)
            except self.user_model.DoesNotExist:
                log_message(f"User {username} does not exist.")
                user = None
            else:
                try:
                    session = auth_session_model.objects.get(user=auth_user, token=password, expires_at__gte=aware_now())
                except auth_session_model.DoesNotExist:
                    if settings.DEBUG:
                        log_message(f"Session with token {password} does not exist.")

                    user = None
                else:
                    user = session.user

        return user
