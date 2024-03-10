import mimetypes
import os
import re
from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from accounts.lib_utils import log_message, is_empty, not_empty


def base_email_context(request=None) -> dict:
    context = dict()

    if not_empty(request):
        current_site = Site.objects.get_current(request)

        request_uri = request.build_absolute_uri()
        url = urlsplit(request_uri)
        site_url = "%s://%s" % (url.scheme, url.hostname)

        context["site_url"] = site_url
        context["site_name"] = current_site.name
        context["company_name"] = current_site.name

    return context


def email_to_dict(value) -> dict:
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

    if not isinstance(to_list, list):
        to_list = [to_list]

    fail_silently = kwargs.get("fail_silently", False)

    attachments = kwargs.get("attachments", False)

    request = kwargs.get("request", None)

    context = kwargs.get("context", dict())

    html_message = kwargs.get("html_message", None)

    html_template_path = kwargs.get("html_template", None)
    html_context = kwargs.get("html_context", context)

    if not_empty(html_template_path) and isinstance(html_context, dict):
        if debug:
            log_message("rendering html template.")

        html_context.update(base_email_context(request))

        if ".html" not in html_template_path:
            html_template_path = f"{html_template_path}.html"
        else:
            html_template_path = html_template_path

        html_message = get_template(html_template_path).render(html_context)

    text_message = kwargs.get("text_message", None)

    text_template_path = kwargs.get("text_template", None)
    text_context = kwargs.get("text_context", context)

    if not_empty(text_template_path) and not_empty(text_context):
        if debug:
            log_message("rendering text template.")

        text_context.update(base_email_context(request))

        if ".txt" not in text_template_path:
            text_template_path = f"{text_template_path}.txt"
        else:
            text_template_path = text_template_path

        text_message = get_template(text_template_path).render(text_context)

    if is_empty(html_message) and not_empty(text_message):
        if debug:
            log_message("Using text message as html message.")

        html_message = re.sub(
            r"(http.*?)\s", r'<a href="\g<1>">\<g>1</a>', "<p>" + "</p><p>".join(text_message.split("\n")) + "</p>"
        )

    if debug:
        log_message(text_message)
        log_message(html_message)

    if debug:
        log_message(f"Send multipart email to: {to_list}.")

    if not isinstance(from_str, str):
        if debug:
            log_message("Sending from default sender.")
        from_str = settings.DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject_str, text_message, from_str, to_list)

    if not is_empty(html_message):
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

    if not_empty(url) and not_empty(token):
        if is_empty(title):
            title = "Notification from {}".format(settings.SITE_NAME)

        if not_empty(url) and not_empty(token):
            resp = requests.post(
                f"{url}/message?token={token}", json={"message": message, "priority": 2, "title": title}
            )
