import datetime
import io
import json

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import models
from django.http import HttpResponse
from requests_oauthlib import OAuth2Session

from accounts.auth_helper import MSAuth, MSGraph
from accounts.utils import is_empty, log_message, aware_now, not_empty


class ExtendedUser(models.Model):
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.DO_NOTHING
    )
    ms_id = models.CharField(max_length=255, blank=True, null=True)
    business_phones = models.JSONField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile_phone = models.CharField(max_length=50, blank=True, null=True)
    office_location = models.CharField(max_length=255, blank=True, null=True)
    preferred_language = models.CharField(max_length=50, blank=True, null=True)
    user_principal_name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(blank=True, null=True, upload_to="profile_pics")
    user_json = models.JSONField(blank=True, null=True)

    class Meta:
        permissions = (
            (
                "is_tester",
                "User is a tester, and can see parts of the site open for testing purposes",
            ),
            (
                "is_developer",
                "User is a developer and can see parts of the site for developers only",
            ),
        )

    def __str__(self):
        if isinstance(self.user_principal_name, str):
            return self.user_principal_name
        elif not is_empty(self.user) and isinstance(self.user.email, str):
            return self.user.email

        return super().__str__()

    @classmethod
    def create_from_response(cls, auth_user, user):
        principal_name = user.get("userPrincipalName")

        try:
            u = cls.objects.get(user_principal_name=principal_name)
        except cls.DoesNotExist:
            u = cls.objects.create(
                user=auth_user,
                ms_id=user.get("id"),
                business_phones=user.get("businessPhones"),
                name=user.get("displayName"),
                first_name=user.get("givenName"),
                last_name=user.get("surname"),
                title=user.get("jobTitle"),
                email=user.get("mail"),
                mobile_phone=user.get("mobilePhone"),
                office_location=user.get("officeLocation"),
                preferred_language=user.get("preferredLanguage"),
                user_principal_name=principal_name,
                user_json=user,
            )
        else:
            u.ms_id = user.get("id")
            u.business_phones = user.get("businessPhones")
            u.name = user.get("displayName")
            u.first_name = user.get("givenName")
            u.last_name = user.get("surname")
            u.title = user.get("jobTitle")
            u.email = user.get("mail")
            u.mobile_phone = user.get("mobilePhone")
            u.office_location = user.get("officeLocation")
            u.preferred_language = user.get("preferredLanguage")
            u.user_principal_name = user.get("userPrincipalName")
            u.user_json = user
            u.save()

        return u

    @property
    def session(self):
        try:
            return GraphSession.objects.get(user=self.user, expires_at__gte=aware_now())
        except GraphSession.DoesNotExist as e:
            log_message(f"Session not found for {self.user}")
            return None

    def get_photo(self):
        photo = self.session.graph.get_user_photo()

        if is_empty(self.photo) and not is_empty(photo):
            image_file = io.BytesIO(photo.content)
            self.photo.save(f"{self.ms_id}.jpg", image_file)
            self.save()

        return photo


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

    @property
    def graph(self):
        return MSGraph(self.token)

    @property
    def refresh_token(self):
        return self.token.get("refresh_token")

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

    def get_photo(self):
        photo = self.graph_client.get(f"{self.graph_url}/me/photo/$value")

        if "error" not in photo.content.decode():
            return photo.content

        else:
            resp = None

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

    @property
    def user_profile(self):
        try:
            return ExtendedUser.objects.get(user=self.user)

        except ExtendedUser.DoesNotExist:
            g = MSGraph(self.token)
            return ExtendedUser.create_from_response(self.user, g.get_user())

        except ExtendedUser.MultipleObjectsReturned:
            g = MSGraph(self.token)
            return g.get_user()

        return None
