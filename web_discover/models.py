import datetime
import socket
import ssl
from urllib.parse import urlsplit, parse_qs

import requests
import xmltodict
from bs4 import BeautifulSoup
from django.contrib.postgres.fields import JSONField
from django.db.models import (
    Model,
    CharField,
    IntegerField,
    DateTimeField,
    FloatField,
    URLField,
    TextField,
)

from web_discover.constants import DEFAULT_SSL_PORT
from web_discover.helpers import convert_keys, to_dict


class SSLCert(Model):
    ssl_info = JSONField(blank=True)

    domain = CharField(max_length=255, blank=True, null=True)
    port = IntegerField(null=True)
    timeout = FloatField(null=True, default=3.0)
    ssl_port = IntegerField(null=True, default=DEFAULT_SSL_PORT)

    issuer = JSONField(blank=True)
    subject = CharField(max_length=255, blank=True, null=True)

    expires = DateTimeField(null=True)
    days_left = CharField(max_length=255, blank=True, null=True)

    ssl_date_fmt = r"%b %d %H:%M:%S %Y %Z"

    @property
    def cert_key(self):

        return "CERT_{0}".format(self.domain)

    def update_ssl(self):
        context = ssl.create_default_context()
        conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.domain)
        conn.settimeout(self.timeout)

        conn.connect((self.domain, self.ssl_port))
        self.ssl_info = conn.getpeercert()

        for k, v in self.ssl_info.items():
            if isinstance(v, (list, tuple)):
                new_val = dict()
                for pair in v:
                    try:
                        key = pair[0][0]
                        val = pair[0][1]
                    except Exception as e:
                        new_val = v

                    else:
                        new_val[key] = val

                self.ssl_info[k] = new_val

        self.issuer = self.ssl_info.get("issuer")
        self.subject = self.ssl_info.get("subject")
        self.expires = datetime.datetime.strptime(self.ssl_info["notAfter"], self.ssl_date_fmt)

        self.save()

    def life_time_remaining(self) -> datetime.timedelta:
        """
        Returns the number of days until ssl certificate expires

        :return: datetime.timedelta
        """
        self.days_left = self.expires - datetime.datetime.utcnow()
        self.save()

        return self.days_left


class WebSite(Model):
    url = URLField(blank=True, null=True)

    protocol = CharField(max_length=50, blank=True, null=True)
    domain = CharField(max_length=255, blank=True, null=True)
    port = IntegerField(null=True)

    site_url = CharField(max_length=255, blank=True, null=True)
    base_url = CharField(max_length=255, blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        url = urlsplit(self.url)

        self.protocol = url.scheme
        self.domain = url.hostname
        self.port = url.port

        if self.protocol and not self.port:
            if self.protocol == "https":
                self.port = 443
            elif self.protocol == "http":
                self.port = 80

        # Without Slash
        if self.port and self.port not in [80, 443]:
            self.site_url = "%s://%s:%s" % (self.protocol, self.domain, str(self.port))
        else:
            self.site_url = "%s://%s" % (self.protocol, self.domain)

        self.base_url = "%s/" % self.site_url  # With slash

        super(WebSite, self).save(force_insert, force_update, using, update_fields)

    @property
    def cert(self):
        try:
            retn = SSLCert.objects.get(domain=self.domain)
        except SSLCert.DoesNotExist:
            retn = SSLCert.objects.create(domain=self.domain)
            retn.update_ssl()

        return retn

    def get_external_url(self, resource_path):
        """
        Returns a fully qualified web address fo a resource.

        :param resource_path: A site relative path.
        :return: A url that includes the full site url to the resource
        """
        urlbase = self.base_url

        if resource_path[0] in ["/", "\\"]:
            urlbase = self.site_url

        external_url = "%s%s" % (urlbase, resource_path)

        return external_url

    def get_sitemap(self):
        sitemap_urls = []

        sitemap_url = "{0}/{1}".format(self.site_url, "sitemap.xml")
        resp = requests.get(sitemap_url)

        if resp.status_code == 200:
            sitemap_xml = resp.text
            sitemap_dict = convert_keys(to_dict(xmltodict.parse(sitemap_xml)))

            urlset = sitemap_dict.get("urlset", {}).get("url")

            for url in urlset:
                sitemap_urls.append(url.get("loc"))

        return sitemap_urls


class WebPath(Model):
    url = TextField(blank=True, null=True)

    request_path = CharField(max_length=255, blank=True, null=True)
    fragment = CharField(max_length=255, blank=True, null=True)
    query = JSONField(blank=True, null=True)
    params = JSONField(blank=True, null=True)
    canonical_url = CharField(max_length=255, blank=True, null=True)
    status_code = IntegerField(null=True)
    page_source = TextField(null=True)

    @property
    def domain(self):
        url = urlsplit(self.url)

        return url.hostname

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.url:
            url = urlsplit(self.url)
            domain = url.hostname

            self.request_path = url.path
            self.fragment = url.fragment
            self.query = url.query
            self.params = parse_qs(self.query)

            self.canonical_url = self.website.get_external_url(self.request_path)

        super(WebPath, self).save(force_insert, force_update, using, update_fields)

    @property
    def get_url(self):
        if self.canonical_url:
            return self.canonical_url
        else:
            return self.url

    @property
    def website(self):
        try:
            retn = WebSite.objects.get(domain=self.domain)
        except WebSite.DoesNotExist:
            url = urlsplit(self.url)

            if url.port and url.port not in [80, 443]:
                site_url = "%s://%s:%s" % (url.scheme, self.domain, str(url.port))
            else:
                site_url = "%s://%s" % (url.scheme, self.domain)

            WebSite.objects.create(url=site_url, site_url=site_url, domain=self.domain, port=url.port)
            retn = WebSite.objects.get(domain=self.domain)

        return retn

    @property
    def code(self):
        resp = requests.get(self.get_url)
        self.status_code = resp.status_code
        self.save()

        return self.status_code

    @property
    def html(self):
        if not self.status_code:
            resp = requests.get(self.get_url, params=self.params)
            self.status_code = resp.status_code
            self.page_source = resp.text
            self.save()

        return self.page_source

    @property
    def links(self):
        soup = BeautifulSoup(self.html, "html.parser")
        link_list = soup.find_all("a")

        retn_list = []
        for link in link_list:
            href = link.get("href")

            if isinstance(href, str) and len(href) > 0 and "mailto" not in href:
                if "http" not in href:
                    href = self.website.get_external_url(href)

                if self.website.site_url in href:
                    try:
                        href_path = WebPath.objects.get(canonical_url__istartswith=href)
                    except WebPath.DoesNotExist:
                        WebPath.objects.create(url=href)
                        href_path = WebPath.objects.get(canonical_url__istartswith=href)

                    retn_list.append(href_path.canonical_url)

        return list(set(retn_list))

    @property
    def webpaths(self):
        return (WebPath(x) for x in self.links)
