from django.db import models


class PostalCode(models.Model):
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
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )  # estimated latitude (wgs84)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, blank=True, null=True
    )  # estimated longitude (wgs84)
    accuracy = models.IntegerField(
        null=True
    )  # accuracy of lat/lng from 1=estimated, 4=geonameid, 6=centroid of addresses or shape
    distance = models.FloatField(null=True)  # Always overwritten in distance queries

    def __str__(self):

        return self.place_name

    # def within_radius(self, radius, **kwargs):

