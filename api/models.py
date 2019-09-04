from django.db import models
from django.db.models import Model, IntegerField, CharField, ForeignKey, DecimalField, IPAddressField, BooleanField, \
    DO_NOTHING

from api.constants import ACCURACY_CHOICES
from gis.models import GISPoint


class PostalCode(GISPoint):
    country_code = models.CharField(max_length=2, blank=True, null=True)  # iso country code, 2 characters
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # varchar(20)
    place_name = models.CharField(max_length=180, blank=True, null=True)  # varchar(180)
    admin_name1 = models.CharField(max_length=100, blank=True, null=True)  # 1. order subdivision (state) varchar(100)
    admin_code1 = models.CharField(max_length=20, blank=True, null=True)  # 1. order subdivision (state) varchar(20)
    admin_name2 = models.CharField(
        max_length=100, blank=True, null=True
    )  # 2. order subdivision (county/province) varchar(100)
    admin_code2 = models.CharField(
        max_length=20, blank=True, null=True
    )  # 2. order subdivision (county/province) varchar(20)
    admin_name3 = models.CharField(
        max_length=100, blank=True, null=True
    )  # 3. order subdivision (community) varchar(100)
    admin_code3 = models.CharField(max_length=20, blank=True, null=True)  # 3. order subdivision (community) varchar(20)
    accuracy = models.IntegerField(
        null=True, choices=ACCURACY_CHOICES
    )  # accuracy of lat/lng from 1=estimated, 4=geonameid, 6=centroid of addresses or shape
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.place_name


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
