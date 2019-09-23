from django.db import models
from django.db.models import (
    Model,
    CharField,
    BooleanField,
)
from geo_ez.models import GISPoint


class IP4Location(GISPoint):
    network = CharField(max_length=128)
    geoname_id = CharField(max_length=180, blank=True, null=True)
    registered_country_geoname_id = CharField(max_length=180, blank=True, null=True)
    represented_country_geoname_id = CharField(max_length=180, blank=True, null=True)
    is_anonymous_proxy = BooleanField(default=False)
    is_satellite_provider = BooleanField(default=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # varchar(20)
    updated = models.DateTimeField(auto_now_add=True, null=True)


class IP6Location(GISPoint):
    network = CharField(max_length=255)
    geoname_id = CharField(max_length=180, blank=True, null=True)
    registered_country_geoname_id = CharField(max_length=180, blank=True, null=True)
    represented_country_geoname_id = CharField(max_length=180, blank=True, null=True)
    is_anonymous_proxy = BooleanField(default=False)
    is_satellite_provider = BooleanField(default=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # varchar(20)
    updated = models.DateTimeField(auto_now_add=True, null=True)
