import mimetypes
import os
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from accounts.lib_utils import log_message, is_empty, not_empty


def base_email_context(request):
    context = dict()

    current_site = Site.objects.get_current(request)

    request_uri = request.build_absolute_uri()
    url = urlsplit(request_uri)
    site_url = "%s://%s" % (url.scheme, url.hostname)

    context["site_url"] = site_url
    context["site_name"] = current_site.name
    context["company_name"] = current_site.name

    return context


def email_to_dict(value):
    if "<" in value and ">" in value:
        name = value.split("<")[0].strip()
        email = value.split("<")[1][0:-1]
    else:
        name = value.split("@")[0]
        email = value

    return dict(name=name, email=email)


def send_multipart_email(subject_str, to_list, from_str, **kwargs):
    """Send a single html email message (which can be sent to multiple recipients).

        subject_str = String to use as email subject
        to_list = list of recipient email address strings
        from_str = string to use as the from email address
        template_path = path, from webroot to the email template to use, .html type
        context_dict = dictionary defining any variables that are required to fully render the template."""

    debug = getattr(settings, "DEBUG", False)

    fail_silently = kwargs.get("fail_silently", False)

    attachments = kwargs.get("attachments", False)

    html_message = kwargs.get("html_message", None)

    html_template_path = kwargs.get("html_template", None)
    html_context = kwargs.get("html_context", None)

    if not_empty(html_template_path) and not_empty(html_context):
        if ".html" not in html_template_path:
            html_template_path = f"{html_template_path}.html"
        else:
            html_template_path = html_template_path

        if kwargs.get("request") is not None:
            if isinstance(html_context, dict):
                html_context.update(base_email_context(kwargs.get("request")))
        else:
            if not isinstance(html_context, dict):
                html_context = {}

        html_message = get_template(html_template_path).render(html_context)

    text_message = kwargs.get("text_message", None)

    text_template_path = kwargs.get("text_template", None)
    text_context = kwargs.get("context", None)

    if not_empty(text_template_path) and not_empty(text_context):
        if ".html" not in text_template_path:
            text_template_path = f"{text_template_path}.txt"
        else:
            text_template_path = text_template_path

        if kwargs.get("request") is not None:
            if isinstance(text_context, dict):
                text_context.update(base_email_context(kwargs.get("request")))
        else:
            if not isinstance(text_context, dict):
                text_context = {}

        text_message = get_template(text_template_path).render(text_context)

    if not is_empty(text_message) and is_empty(html_message):
        html_message = "<p>" + "</p><p>".join(text_message.split("\n")) + "</p>"

    if debug:
        log_message(f"Send multipart email to: {to_list}.")

    if not isinstance(from_str, str):
        if debug:
            log_message("Sending from default sender.")
        from_str = settings.DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject_str, text_message, from_str, to_list)

    if not is_empty(html_message):
        html_message = get_template(html_template_path).render(html_context)
        msg.attach_alternative(html_message, "text/html")

    if isinstance(attachments, list):
        mimetypes.init()
        for attachment in attachments:
            msg.attach(os.path.basename(attachment), open(attachment, "rb").read(), mimetypes.guess_type(attachment)[0])

    result = msg.send(fail_silently)

    return result


def email_user(user, subject, message, from_email=None, **kwargs):
    log_message("Sending Multipart email to {}".format(user.email))
    return send_multipart_email(subject, [user.email], from_email, text_message=message, **kwargs)


def send_push(message, title=None):
    url = getattr(settings, "GOTIFY_URL")
    token = getattr(settings, "GOTIFY_TOKEN")

    if is_empty(title):
        title = "Notification from {}".format(settings.SITE_NAME)

    if not_empty(url) and not_empty(token):
        resp = requests.post(f'{url}/message?token={token}', json={
            "message": message,
            "priority": 2,
            "title": title
        })
