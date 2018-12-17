from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from future.backports.urllib.parse import urlparse


def website_context(request):
    """Site wide content processor, returns a dictionary of values to be
       available site wide. Use with caution as queries here will affect site
       performance."""
    return_dict = {}
    site_name = ''

    try:
        current_site = Site.objects.get_current(request)
    except Site.DoesNotExist:
        if settings.SITE_ID:
            current_site = Site.objects.get(pk=settings.SITE_ID)

    site_url = current_site.domain

    proto = 'https'
    if settings.SITE_PROTO:
        proto = getattr(settings, 'SITE_PROTO', 'https')

    # Force these attributes to be set in the settings, so both get_generic_context and kph_api_request
    # in portal_user will work on multiple domains.
    settings_domain = getattr(settings, 'DOMAIN_NAME', '')
    if settings_domain == '' or settings_domain != site_url:
        setattr(settings, 'DOMAIN_NAME', site_url)

    settings_url = getattr(settings, 'SITE_URL', '')
    if settings_url == '' or settings_url != '%s://%s' % (proto, site_url):
        setattr(settings, 'SITE_URL', '%s://%s' % (proto, site_url))

    domain = urlparse(site_url)
    return_dict = {
        'site_url': '%s://%s' % (proto, site_url),
        'domain_name': domain.netloc.title(),
        'site_name': current_site.name
    }

    return return_dict
