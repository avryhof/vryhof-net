from django.db import models


class GISPoint(models.Model):
    name = models.CharField(max_length=180, blank=True, null=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    distance = models.FloatField(null=True)  # Always overwritten in distance queries

    class Meta:
        abstract = True

    def __str__(self):
        return "%s,%s" % (str(self.latitude), str(self.longitude))

    def distance_from(self, latitude, longitude, **kwargs):
        if kwargs.get('use_miles', True):
            distance_unit = 3959
        else:
            distance_unit = 6371

        sql = 'SELECT id, latitude, longitude, ' \
              '(%f * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - ' \
              'radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) AS distance ' \
              'FROM api_postalcode WHERE id = %i;' % (
                  distance_unit,
                  str(latitude),
                  str(longitude),
                  str(latitude),
                  self.id
              )

        for point in self.objects.raw(sql):
            return point.distance

    def in_radius(self, latitude, longitude, radius, **kwargs):
        if kwargs.get('use_miles', True):
            distance_unit = 3959
        else:
            distance_unit = 6371

        return self.distance_from(latitude, longitude, **kwargs) < radius