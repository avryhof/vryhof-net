from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.urls import NoReverseMatch
from rest_framework import status

from .auth_helper import MSAuth, MSGraph
from .cookies import set_cookie_in_response, get_cookie_in_request
from .utils import not_empty, load_model, is_empty


def sign_in(request, *args, **kwargs):
    msauth = MSAuth(request, debug=True)

    next_url = request.GET.get("next")

    if msauth.user_session:
        user = authenticate(username=msauth.user_session.user.username, password=msauth.user_session.user.password)
        login(request, user, backend="accounts.backends.MSGraphBackend")

        resp = HttpResponseRedirect(request.META["HTTP_REFERER"])

    else:
        # Get the sign-in URL
        sign_in_url, state = msauth.get_sign_in_url()
        # Save the expected state so we can validate in the callback
        request.session["auth_state"] = state
        # Redirect to the Azure sign-in page

        resp = HttpResponseRedirect(sign_in_url)

    resp = set_cookie_in_response(resp, "next_url", next_url, 1)

    return resp


def callback(request):
    session_model = load_model("accounts.GraphSession")

    msauth = MSAuth(request)

    # Get the state saved in session
    expected_state = request.session.pop("auth_state", "")
    # Make the token request
    token = msauth.get_token_from_code(request.get_full_path(), expected_state)
    # Save token and user
    # msauth.store_token(token=token)

    # Get the user's profile
    g = MSGraph(token)
    user_json = g.get_user()
    auth_user = msauth.store_user(user_json)

    remote_session = session_model.get_or_create_session(token, request, is_authenticated=True)
    if is_empty(remote_session.user):
        session_model.objects.filter(user=auth_user).exclude(pk=remote_session.pk).delete()

        remote_session.user = auth_user
        remote_session.save()

    msauth.user_session = remote_session

    print(remote_session.user)

    authenticated_user = authenticate(username=remote_session.user.username, password=remote_session.user.password)
    login(request, authenticated_user, backend="accounts.backends.MSGraphBackend")

    next_url = get_cookie_in_request(request, "next_url")

    resp = redirect(settings.LOGIN_REDIRECT_URL)
    if not_empty(next_url):
        try:
            resp = redirect(next_url)
        except NoReverseMatch:
            pass

    return resp


def sign_out(request):
    msauth = MSAuth(request)
    # Clear out the user and token
    msauth.remove_user_and_token()

    return redirect(settings.LOGIN_REDIRECT_URL)


def get_photo(request, **kwargs):
    width = kwargs.get("width", False)
    height = kwargs.get("height", False)

    msauth = MSAuth(request)
    token = msauth.get_token()

    if token:
        g = MSGraph(token)
        photo = g.get_user_photo(width=width, height=height)

    else:
        photo = HttpResponse()
        photo.status_code = status.HTTP_404_NOT_FOUND

    return photo
