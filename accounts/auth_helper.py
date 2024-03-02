import datetime
import json
import os
import random
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.urls import reverse
from requests_oauthlib import OAuth2Session

from accounts.utils import aware_now, log_message, load_model, is_empty


class MSAuth:
    debug = False

    tenant_url = "https://login.microsoftonline.com/common"
    authorize_url = None
    token_url = None

    MINUTE = 60

    application_key = None
    application_password = None

    application_authority = None
    authorize_endpoint = None
    token_endpoint = None

    application_scopes = None
    application_redirect = None

    aad_auth = None

    sign_in_url = None
    state = False

    user_model = None
    user_session = None
    user = None
    request = None
    token = False
    expire_time = None

    session_model = None

    def __init__(self, request, **kwargs):
        self.debug = kwargs.get("debug", False)

        self.request = request
        self.user_model = get_user_model()
        self.session_model = load_model("accounts.GraphSession")

        secure_transport = kwargs.get("secure_transport", getattr(settings, "MS_SECURE_TRANSPORT", False))
        relax_token_scope = kwargs.get("relax_token_scope", getattr(settings, "MS_RELAX_TOKEN_SCOPE", False))
        ignore_scope_change = kwargs.get("ignore_scope_change", getattr(settings, "MS_IGNORE_SCOPE_CHANGE", False))

        if not secure_transport:
            # This is necessary for testing with non-HTTPS localhost
            # Remove this if deploying to production
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        else:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

        self._debug(secure_transport, os.environ["OAUTHLIB_INSECURE_TRANSPORT"])

        # This is necessary because Azure does not guarantee
        # to return scopes in the same case and order as requested
        if relax_token_scope:
            os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

        if ignore_scope_change:
            os.environ["OAUTHLIB_IGNORE_SCOPE_CHANGE"] = "1"

        self.application_authority = getattr(settings, "MS_AUTHORITY", "https://login.microsoftonline.com/common")
        self.authorize_endpoint = getattr(settings, "MS_AUTHORIZE_ENDPOINT", "/oauth2/v2.0/authorize")
        self.token_endpoint = getattr(settings, "MS_TOKEN_ENDPOINT", "/oauth2/v2.0/token")

        tenant_id = getattr(settings, "MS_TENANT_ID")

        if is_empty(tenant_id):
            self._debug("Tenant ID is empty")

        self.tenant_url = f"https://login.microsoftonline.com/{tenant_id}"

        self.authorize_url = "%s%s" % (self.tenant_url, self.authorize_endpoint)
        self.token_url = "%s%s" % (self.tenant_url, self.token_endpoint)

        self.application_key = getattr(settings, "MS_CLIENT_ID")
        self.application_password = getattr(settings, "MS_CLIENT_SECRET")

        self.application_scopes = getattr(settings, "MS_SCOPE",
                                          ["openid", "profile", "offline_access", "user.read", "User.ReadBasic.All"])

        self.application_redirect = self.get_callback_url()

        self.token = request.session.get("token", False)

        if self.request.user.is_authenticated and is_empty(self.token):
            self.user_session = self.session_model.objects.filter(user=self.request.user).latest("expires_at")
            self.token = self.user_session.token

        if self.token:
            self.user_session = self.session_model.get_or_create_session(self.token, request)
            self.user = self.user_session.user

    def _debug(self, *messages):
        message_parts = ["[MS AUTH HELPER]"]
        for message in messages:
            message_parts.append(str(message))

        log_message(" ".join(message_parts))

        if self.debug:
            print(log_message)

    def get_callback_url(self):
        callback_url = os.environ.get("APPLICATION_REDIRECT")

        if is_empty(callback_url):
            url = urlparse(self.request.build_absolute_uri())
            port = url.port

            if is_empty(port):
                if not is_empty(getattr(settings, "FORCE_PORT")):
                    port = settings.FORCE_PORT
                elif url.scheme == "https":
                    port = 443
                else:
                    port = 80

            if int(port) not in [80, 443]:
                callback_url = f"{url.scheme}://{url.hostname}:{url.port}{reverse('callback')}"
            else:
                callback_url = f"{url.scheme}://{url.hostname}{reverse('callback')}"

        self._debug("CALLBACK URL: %s" % callback_url)

        return callback_url

    def get_aad_auth(self, **kwargs):
        token = kwargs.get("token", self.token)
        state = kwargs.get("state", self.state)

        if token != self.token:
            self.token = token

        if state != self.state:
            self.state = state

        aad_auth = None

        if self.application_scopes and self.application_redirect and self.application_key:

            in_args = dict(scope=self.application_scopes, redirect_uri=self.application_redirect)
            if state:
                in_args.update(dict(state=state))

            if token:
                if not isinstance(token, dict):
                    token = json.loads(token.replace("'", '"'))

                in_args.update(dict(token=token))

            aad_auth = OAuth2Session(self.application_key, **in_args)

        self.aad_auth = aad_auth

        return aad_auth

    def get_sign_in_url(self):
        # Method to generate a sign-in url
        # Initialize the OAuth client
        aad_auth = self.get_aad_auth(sign_in=True)

        sign_in_url, state = aad_auth.authorization_url(self.authorize_url, prompt="login")

        self.sign_in_url = sign_in_url
        self.state = state

        return sign_in_url, state

    def get_token_from_code(self, callback_url, expected_state):
        # Method to exchange auth code for access token
        # Initialize the OAuth client
        self.aad_auth = self.get_aad_auth(state=expected_state)
        self.token = self.aad_auth.fetch_token(
            self.token_url, client_secret=self.application_password, authorization_response=callback_url
        )
        return self.token

    def get_or_create_session(self):
        # Delete old sessions
        self.session_model.objects.filter(user=self.user, expires_at__lt=aware_now()).delete()

        expires = aware_now() + datetime.timedelta(seconds=self.token.get("expires_in"))

        self.user_session = self.session_model.get_or_create_session(
            str(self.token),
            self.request,
            user=self.user,
            is_authenticated=True,
            access_token=self.token.get("access_token"),
            expires_at=expires,
        )

        return self.user_session

    def get_or_create_user(self, **kwargs):
        username = kwargs.get("username")
        email = kwargs.get("email")
        name = kwargs.get("name")
        first_name = kwargs.get("first_name", name.split(" ")[0])
        last_name = kwargs.get("last_name", name.split(" ")[1])

        try:
            self.user = self.user_model.objects.get(
                username=username, email=email, first_name=first_name, last_name=last_name
            )
        except self.user_model.DoesNotExist:
            self.user = self.user_model(
                username=username, email=email, first_name=first_name, last_name=last_name, is_active=True
            )
            # We don't actually use the password stored in the user_model
            self.user.set_password("%x" % random.randint(0, 2 ** 256))
            self.user.save()

        if not self.user.id:
            if self.request.user.id:
                self._debug("User is logged in.")
                self.user = self.request.user

            elif self.user_session and self.user_session.user:
                self._debug("Using existing session user.")
                self.user = self.user_session.user

            elif self.user_session.email:
                try:
                    self._debug("Email match.")
                    self.user = self.user_model.objects.get(email=self.user_session.email)
                except self.user_model.DoesNotExist:
                    pass

        self._debug("Returning %s." % self.user)

        return self.user

    def store_token(self, **kwargs):
        token = kwargs.get("token", self.token)

        if token != self.token:
            self.token = token

        self.request.session["token"] = token

        self.get_or_create_session()
        # self.user_session.token = self.token
        # self.user_session.save()

    def store_user(self, user):
        self.request.session["user"] = user

        email = user.get("mail")
        if is_empty(email):
            email = user.get("userPrincipalName")

        return self.get_or_create_user(
            username=user.get("userPrincipalName"),
            email=email,
            name=user.get("displayName"),
            first_name=user.get("givenName"),
            last_name=user.get("surname"),
        )

    def get_token(self):
        token = self.token

        if self.user_session and not self.user_session.expired:
            token = self.user_session.token
        else:
            # Refresh the token
            aad_auth = self.get_aad_auth(token=token)

            refresh_params = {
                "client_id": self.application_key,
                "client_secret": self.application_password,
                "refresh_token": token.get("refresh_token"),
            }
            new_token = aad_auth.refresh_token(self.token_url, **refresh_params)

            # Save new token
            self.store_token(token=new_token)
            token = new_token

        return token

    def remove_user_and_token(self):
        self.request.session["token"] = None
        self.request.session["user"] = None
        self.user = None
        self.token = None

        if self.user_session:
            self.user_session.delete()

        logout(self.request)
        self.request.session.flush()


class MSGraph:
    debug = False

    user_session = None
    auth_user = None

    graph_url = None
    token = None

    request = None

    def __init__(self, token, **kwargs):
        self.debug = kwargs.pop("debug", False)

        self.user_session = kwargs.pop("user_session", None)
        self.request = kwargs.get("request", None)

        if is_empty(self.user_session):
            session_model = load_model("accounts.GraphSession")
            self.user_session = session_model.get_or_create_session(token, self.request)

        self.graph_url = self.user_session.graph_url
        self.token = self.user_session.token
        self.graph_client = self.user_session.graph_client
        self.auth_user = self.user_session.user

    def get_user(self):
        return self.user_session.get_user()

    def get_user_photo(self):
        return self.user_session.get_photo()

    def get_group_membership(self):
        return self.user_session.get_group_membership()

    def get_calendar_events(self):
        return self.user_session.get_calendar_events()

    def get_email_messages(self):
        return self.user_session.get_email_messages()
