import mimetypes
import os
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from accounts.lib_utils import log_message


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


def send_multipart_email(subject_str, to_list, from_str, template_path, context_dict, **kwargs):
    """Send a single html email message (which can be sent to multiple recipients).

        subject_str = String to use as email subject
        to_list = list of recipient email address strings
        from_str = string to use as the from email address
        template_path = path, from webroot to the email template to use, .html type
        context_dict = dictionary defining any variables that are required to fully render the template."""

    debug = kwargs.get("debug", False)
    fail_silently = kwargs.get("fail_silently", False)

    attachments = kwargs.get("attachments", False)
    is_html = kwargs.get("html", True)

    if debug:
        log_message(f"Send multipart email to: {to_list}.")

    if kwargs.get("request") is not None:
        if isinstance(context_dict, dict):
            context_dict.update(base_email_context(kwargs.get("request")))
    else:
        if not isinstance(context_dict, dict):
            context_dict = {}

    if not isinstance(from_str, str):
        if debug:
            log_message("Sending from default sender.")
        from_str = settings.DEFAULT_FROM_EMAIL

    text_template_path = f"{template_path}.txt"
    try:
        text_message = get_template(text_template_path).render(context_dict)
    except TemplateDoesNotExist:
        text_message = context_dict.get("message")

    msg = EmailMultiAlternatives(subject_str, text_message, from_str, to_list)

    if is_html:
        if ".html" not in template_path:
            html_template_path = f"{template_path}.html"
        else:
            html_template_path = template_path

        html_message = get_template(html_template_path).render(context_dict)
        msg.attach_alternative(html_message, "text/html")

    if isinstance(attachments, list):
        mimetypes.init()
        for attachment in attachments:
            msg.attach(os.path.basename(attachment), open(attachment, "rb").read(), mimetypes.guess_type(attachment)[0])

    result = msg.send(fail_silently)

    return result


def email_user(user, subject, message, from_email=None, **kwargs):
    log_message("Sending Multipart email to {}".format(user.email))
    return send_multipart_email(subject, [user.email], from_email, message, **kwargs)
