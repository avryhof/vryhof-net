import datetime
import random
import string
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.sessions.models import Session
from django.db import models
from django.urls import reverse

from accounts.lib_utils import aware_now, log_message


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

        return True


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
        self.expires_at = aware_now() + datetime.timedelta(
            minutes=settings.AUTH_SESSION_LIFETIME
        )
        self.save()

        if settings.DEBUG:
            log_message(f"Token: {self.token}")

        return self.token

    def get_external_url(self, request):
        request_uri = request.build_absolute_uri()
        url = urlsplit(request_uri)
        site_url = "%s://%s" % (url.scheme, url.hostname)

        external_url = "".join(
            [site_url, reverse("login-token", kwargs={"token": self.token})]
        )

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
    photo = models.ImageField(blank=True, null=True)
    pages_open = models.BooleanField(default=True)
    last_url = models.URLField(blank=True, null=True)
