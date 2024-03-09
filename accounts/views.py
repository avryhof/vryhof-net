from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from .forms import LoginForm, LoginTokenForm
from .lib_cookies import set_cookie_in_response, get_cookie_in_request
from .lib_email_helpers import send_multipart_email, send_push
from .lib_utils import load_model, not_empty, random_password, log_message, is_empty


class LoginView(TemplateView):
    template_name = "accounts/login.html"
    extra_css = ["css/accounts/login.css"]
    extra_javascript = []

    name = "Login"
    form = LoginForm

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        form = self.form()

        context["form"] = form

        response = render(request, self.template_name, context)

        next_url = request.GET.get("next")
        if not_empty(next_url):
            response = set_cookie_in_response(response, "next_url", next_url, 1)

        return response

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        form = self.form(request.POST)
        if not form.is_valid():
            log_message(form.errors)

        else:
            user = None

            username = form.cleaned_data.get("username")
            if isinstance(username, str):
                username = username.lower()

            try:
                user = get_user_model().objects.get(email__iexact=username)
            except (
                    get_user_model().DoesNotExist,
                    get_user_model().MultipleObjectsReturned,
            ):
                email_domain_model = load_model("accounts.EmailDomain")
                if not email_domain_model.is_valid_domain(username):
                    log_message("Domain not enabled.")

                else:
                    user = get_user_model().objects.create(
                        username=username,
                        email=username,
                        password=random_password(),
                        is_active=True,
                    )

            if is_empty(user):
                log_message("User does not exist.")

            else:
                auth_session_model = load_model("accounts.AuthSession")
                try:
                    session = auth_session_model.objects.get(user=user)
                except auth_session_model.DoesNotExist:
                    session = auth_session_model.objects.create(user=user)

                token = session.generate_access_token()
                login_link = session.get_external_url(request)

                subject = f"[{settings.EMAIL_PREFIX}] Your login token"
                text_message = f'Your login token is {token}.\n' \
                               f'Enter it at the prompt, or visit {login_link} to log in.'

                send_multipart_email(
                    subject,
                    [user.email],
                    None,
                    text_message=text_message,
                    html_template_path="accounts/email/login-code-email.html",
                    html_context={
                        "code": token,
                        "message": mark_safe(
                            f'<p>Your login token is {token}.</p>'
                            f'<p>Enter it at the prompt, or click <a href="{login_link}">here</a> to log in.</p>'
                        ),
                    },
                )

                send_push(text_message, subject)

                return redirect("login-token")

        context["form"] = form

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginView, self).dispatch(request, *args, **kwargs)


class LoginTokenView(TemplateView):
    template_name = "accounts/login-code.html"
    extra_css = ["css/accounts/login.css"]
    extra_javascript = []

    name = "Login Token"
    form = LoginTokenForm

    def get_context_data(self, **kwargs):
        context = super(LoginTokenView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        if not_empty(kwargs.get("token")):
            form = self.form(initial={"token": kwargs["token"]})
        else:
            form = self.form()

        context["form"] = form

        response = render(request, self.template_name, context)

        next_url = request.GET.get("next")
        if not_empty(next_url):
            response = set_cookie_in_response(response, "next_url", next_url, 1)

        return response

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()

        form = self.form(request.POST)
        if form.is_valid():
            auth_session_model = load_model("accounts.AuthSession")

            session = auth_session_model.check_token(
                request, token=form.cleaned_data["token"]
            )
            if not session:
                return redirect("login")

            next_url = get_cookie_in_request(request, "next_url")

            resp = redirect(settings.LOGIN_REDIRECT_URL)
            if not_empty(next_url):
                try:
                    resp = redirect(next_url)
                except NoReverseMatch:
                    pass

            return resp

        context["form"] = form

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginTokenView, self).dispatch(request, *args, **kwargs)


def sign_out(request):
    request.COOKIES["auth_token"] = ""
    logout(request)
    request.session.flush()

    return redirect(settings.LOGIN_REDIRECT_URL)
