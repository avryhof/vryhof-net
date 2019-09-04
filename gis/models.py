from math import radians, cos, sin, asin, sqrt

from django.db import models


class GISPoint(models.Model):
    name = models.CharField(max_length=180, blank=True, null=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s,%s" % (str(self.latitude), str(self.longitude))

    def distance_from(self, latitude, longitude, **kwargs):
        use_miles = kwargs.get("use_miles", True)
        distance_unit = float(3959 if use_miles else 6371)

        latitude1 = radians(float(latitude))
        latitude2 = radians(float(self.latitude))

        longitude1 = radians(float(longitude))
        longitude2 = radians(float(self.longitude))

        distance_longitude = longitude2 - longitude1
        distance_latitude = latitude2 - latitude1

        a = sin(distance_latitude / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(distance_longitude / 2) ** 2
        c = 2 * asin(sqrt(a))

        distance = c * distance_unit

        return distance

    def in_radius(self, latitude, longitude, radius, **kwargs):

        return self.distance_from(latitude, longitude, **kwargs) < radius
