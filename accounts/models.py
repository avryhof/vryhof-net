import datetime
import random
import string
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.sessions.models import Session
from django.db import models
from django.urls import reverse

from accounts.lib_utils import aware_now, log_message, not_empty, is_empty


class EmailDomain(models.Model):
    enabled = models.BooleanField(default=True)
    site = models.OneToOneField("sites.Site", on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, blank=True, null=True)

    @classmethod
    def is_valid_domain(cls, email):
        if "@" in email:
            email = email.split("@")[1]

            try:
                cls.objects.get(domain__iexact=email, enabled=True)
            except cls.DoesNotExist:
                return False
            else:
                return True

        return False


class AuthSession(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        blank=False,
        null=False,
        primary_key=True,
        on_delete=models.CASCADE,
    )
    is_authenticated = models.BooleanField(default=False)
    token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    @property
    def expired(self):
        if self.expires_at:
            return aware_now() >= self.expires_at

        return True

    def generate_access_token(self):
        valid_chars = string.ascii_letters + string.digits
        length = random.randint(8, 16)

        self.token = "".join(random.choice(valid_chars) for i in range(length))
        self.expires_at = aware_now() + datetime.timedelta(minutes=settings.AUTH_SESSION_LIFETIME)
        self.save()

        if settings.DEBUG:
            log_message(f"Token: {self.token}")

        return self.token

    def get_external_url(self, request):
        request_uri = request.build_absolute_uri()
        url = urlsplit(request_uri)

        if not_empty(url.port) and url.port not in [80, 443]:
            site_url = "{}://{}:{}".format(url.scheme, url.hostname, url.port)
        else:
            site_url = "{}://{}".format(url.scheme, url.hostname)

        external_url = "".join([site_url, reverse("login-token", kwargs={"token": self.token})])

        if settings.DEBUG:
            log_message(f"External login url: {external_url}.")

        return external_url

    @classmethod
    def check_token(cls, request, token):
        try:
            session = cls.objects.get(token=token, expires_at__gte=aware_now())
        except cls.DoesNotExist:
            if settings.DEBUG:
                log_message(f"Session with token {token} does not exist.")
            return False
        else:
            if settings.DEBUG:
                log_message(f"Session with token {token} exists.")

            try:
                user = authenticate(
                    request,
                    username=session.user.username,
                    password=session.token,
                    backend="accounts.backends.AuthTokenBackend",
                )
                login(request, user)

            except Exception:
                if settings.DEBUG:
                    log_message(f"Failed to authenticate user {session.user.username}.")
                session.is_authenticated = False
            else:
                session.is_authenticated = True

            session.save()

            return session.is_authenticated


class UserPrefs(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        blank=False,
        null=False,
        primary_key=True,
        on_delete=models.CASCADE,
    )
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
        after_sync = kwargs.pop("after_sync", False)
        if not after_sync:
            self.sync_user()

        super().save(force_insert, force_update, using, update_fields)

    def sync_user(self):
        self_changed = False
        user_changed = False

        if not_empty(self.user.email) and is_empty(self.email):
            self_changed = True
            self.email = self.user.email

        if not_empty(self.email) and self.user.email != self.email:
            user_changed = True
            self.user.email = self.email

        if not_empty(self.user.first_name) and is_empty(self.first_name):
            self_changed = True
            self.first_name = self.user.first_name

        if not_empty(self.first_name) and self.user.first_name != self.first_name:
            user_changed = True
            self.user.first_name = self.first_name

        if not_empty(self.user.last_name) and is_empty(self.last_name):
            self_changed = True
            self.last_name = self.user.last_name

        if not_empty(self.last_name) and self.user.last_name != self.last_name:
            user_changed = True
            self.user.last_name = self.last_name

        if self_changed:
            self.save(after_sync=True)

        if user_changed:
            self.user.save()

    @property
    def name(self):
        combined_name = " ".join([x for x in [self.first_name, self.last_name] if isinstance(x, str)]).strip()
        if not_empty(combined_name):
            return combined_name

        return self.user.username
