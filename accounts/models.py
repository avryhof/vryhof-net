import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import models
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session

from accounts.auth_helper import MSAuth
from accounts.utils import is_empty, log_message, aware_now, not_empty


class ExtendedUser(models.Model):
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        permissions = (
            ("is_tester", "User is a tester, and can see parts of the site open for testing purposes"),
            ("is_developer", "User is a developer and can see parts of the site for developers only"),
        )

    def __str__(self):
        return self.user


class GraphSession(models.Model):
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.CASCADE)
    is_authenticated = models.BooleanField(default=False)
    access_token = models.TextField(blank=True, null=True)
    token = models.JSONField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    django_session = models.ForeignKey(Session, blank=True, null=True, on_delete=models.CASCADE)
    graph_url = models.URLField(blank=True, null=True, default="https://graph.microsoft.com/v1.0")
    user_json = models.JSONField(blank=True, null=True)

    @property
    def expired(self):
        retn = True

        if self.expires_at:
            return aware_now() >= self.expires_at

        return True

    @property
    def graph_client(self):
        return OAuth2Session(token=self.token)

    @property
    def ms_auth(self):
        return MSAuth(self.token)

    @classmethod
    def get_or_create_session(cls, token, request=None, **kwargs):
        session = None

        if not isinstance(token, dict):
            token = json.loads(token.replace("'", '"'))

        expires_in = token.get("expires_in")
        expires_at = aware_now() + datetime.timedelta(seconds=expires_in)

        access_token = token.get("access_token")

        try:
            session = cls.objects.get(token=token)
        except cls.DoesNotExist:
            if not is_empty(request):
                try:
                    django_session = Session.objects.get(session_key=request.session.session_key)
                except Session.DoesNotExist:
                    pass
                else:
                    session = cls.objects.create(
                        token=token, django_session=django_session, expires_at=expires_at, access_token=access_token
                    )

            else:
                session = cls.objects.create(token=token, expires_at=expires_at, access_token=access_token)

        if not is_empty(session):
            changed = False
            if not_empty(kwargs.get("graph_url")):
                changed = True
                session.graph_url = kwargs.get("graph_url")

            if not_empty(kwargs.get("user")):
                changed = True
                session.user = kwargs.get("user")

            if not_empty(kwargs.get("django_session")):
                changed = True
                session.django_session = kwargs.get("django_session")

            if not_empty(kwargs.get("is_authenticated")):
                changed = True
                session.is_authenticated = kwargs.get("is_authenticated")

            if not_empty(kwargs.get("access_token")):
                changed = True
                session.access_token = kwargs.get("access_token")

            if not_empty(kwargs.get("expires_at")):
                changed = True
                session.expires_at = kwargs.get("expires_at")

            if changed:
                session.save()

        return session

    def get_user(self):
        try:
            user_response = self.graph_client.get("{0}/me".format(self.graph_url))
            self.user_json = user_response.json()

        except Exception as e:
            log_message(e)

        else:
            self.save()

        return self.user_json

    def get_photo(self, width=False, height=False):
        if is_empty(width) and is_empty(height):
            photo = self.graph_client.get("{0}/me/photo/$value".format(self.graph_url))
        else:
            photo = self.graph_client.get("{0}/me/photos/{1}x{2}/$value".format(self.graph_url, width, height))

        resp = HttpResponse(content_type="image/jpg")
        resp.write(photo.content)

        return resp

    def get_group_membership(self):
        groups = self.graph_client.get("{0}/me/memberOf".format(self.graph_url))

        return groups.json()

    def get_calendar_events(self):
        # Configure query parameters to
        # modify the results
        query_params = {"$select": "subject,organizer,start,end", "$orderby": "createdDateTime DESC"}

        # Send GET to /me/events
        events = self.graph_client.get("{0}/me/events".format(self.graph_url), params=query_params)

        return events.json()

    def get_email_messages(self):
        # folders = self.graph_client.get("{0}/me/mailFolders".format(self.graph_url))
        messages = self.graph_client.get("{0}/me/messages".format(self.graph_url))

        return messages.json()
