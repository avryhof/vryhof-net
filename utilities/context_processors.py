from django.conf import settings
from django.contrib.sites.models import Site
from future.backports.urllib.parse import urlparse


def website_context(request):
    return_dict = {}
    site_name = ""

    current_site = None
    try:
        current_site = Site.objects.get_current(request)
    except Site.DoesNotExist:
        if settings.SITE_ID:
            current_site = Site.objects.get(pk=settings.SITE_ID)

    site_url = current_site.domain

    proto = "https"
    if settings.SITE_PROTO:
        proto = getattr(settings, "SITE_PROTO", "https")

    settings_domain = getattr(settings, "DOMAIN_NAME", "")
    if settings_domain == "" or settings_domain != site_url:
        setattr(settings, "DOMAIN_NAME", site_url)

    settings_url = getattr(settings, "SITE_URL", "")
    if settings_url == "" or settings_url != "%s://%s" % (proto, site_url):
        setattr(settings, "SITE_URL", "%s://%s" % (proto, site_url))

    domain = urlparse(site_url)
    return_dict = {
        "site_url": "%s://%s" % (proto, site_url),
        "domain_name": domain.netloc.title(),
        "site_name": current_site.name,
        "signup_enabled": getattr(settings, "SIGNUP_ENABLED")
    }

    return return_dict
