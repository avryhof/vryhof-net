import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from accounts.models import GraphSession
from accounts.utils import log_message, aware_now

logger = logging.getLogger(__name__)
ldap_print_debug = True


class MSGraphBackend(ModelBackend):
    user_model = None

    def __init__(self):
        self.user_model = get_user_model()

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        if username:
            try:
                user = self.user_model.objects.get(username=username)
            except self.user_model.DoesNotExist:
                log_message(f"User {username} does not exist.")
                user = None
            else:
                try:
                    remote_session = GraphSession.objects.get(
                        user=user,
                        is_authenticated=True,
                        expires_at__gt=aware_now()
                    )
                except GraphSession.DoesNotExist:
                    log_message(f"Could not find remote session for {username}")
                    user = None

        return user
