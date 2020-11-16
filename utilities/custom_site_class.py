from urllib.parse import urlsplit, parse_qs

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse


class CustomSite(object):
    protocol = "http"
    domain = None
    request_path = None
    fragment = None
    query = None
    params = None

    site = None
    page = None
    page_slug = None
    homepage = None
    homepage_links = []
    config = None

    site_url = None
    base_url = None
    canonical_url = None

    def __init__(self, request):
        default_uri = settings.SITE_URL
        default_url = urlsplit(default_uri)

        default_protocol = default_url.scheme
        default_domain = default_url.hostname

        request_uri = request.build_absolute_uri()

        url = urlsplit(request_uri)

        self.protocol = url.scheme
        self.domain = url.hostname
        self.request_path = url.path
        self.fragment = url.fragment
        self.query = url.query
        self.params = parse_qs(self.query)

        self.site_url = "%s://%s" % (self.protocol, self.domain)
        self.base_url = "%s/" % self.site_url
        self.canonical_url = "%s/%s" % (self.site_url, self.request_path)

        if hasattr(request, "current_page"):
            self.page = request.current_page

            if hasattr(request.current_page, "get_slug"):
                self.page_slug = request.current_page.get_slug()

        try:
            default_site = Site.objects.get(domain=default_domain)
        except Site.DoesNotExist:
            pass

        if self.domain:
            try:
                self.site = Site.objects.get(domain=self.domain)
            except Site.DoesNotExist:
                try:
                    self.site = Site.objects.get_current(request)
                except Site.DoesNotExist:
                    self.site = Site.objects.get(domain=default_domain)

        # if settings.DEBUG:
        #     log_message("Default Site: %s" % default_domain)
        #     if self.site:
        #         log_message("SITE: %s" % self.site.domain)

        if ".local" in self.domain:
            self.domain = "%s:8000" % self.domain
        setattr(settings, "DOMAIN_NAME", self.domain)

    def external_reverse(self, url_slug, add_slash=False):
        urlbase = self.site_url if not add_slash else self.base_url

        return "%s%s" % (urlbase, reverse(url_slug))
