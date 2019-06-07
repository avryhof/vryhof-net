from django.conf import settings
from django.db import models
from django.db.models import DO_NOTHING, CASCADE
from filer.fields.file import FilerFileField

from geocaching.constants import GPX_CHOICES
from gis.models import GISPoint


class GPXFile(models.Model):
    gpx_file = FilerFileField(null=True, blank=True, on_delete=CASCADE)
    file_type = models.CharField(max_length=64, choices=GPX_CHOICES)
    updated_last_on = models.DateTimeField(auto_now=True, blank=True, editable=False, name='Last Updated')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True, on_delete=DO_NOTHING)

    def __str__(self):

        return self.gpx_file.original_filename


class PocketQuery(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    zip_file = FilerFileField(null=True, blank=True, on_delete=DO_NOTHING)
    geocaches = models.ForeignKey(GPXFile, blank=True, null=True, on_delete=DO_NOTHING, related_name="geocaches")
    waypoints = models.ForeignKey(GPXFile, blank=True, null=True, on_delete=DO_NOTHING, related_name="waypoints")
    updated_last_on = models.DateTimeField(auto_now=True, blank=True, editable=False, name='Last Updated')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True, on_delete=DO_NOTHING)

    def __str__(self):

        return self.name


class Point(GISPoint):
    gpx_files = models.ManyToManyField(GPXFile, blank=True)
    pocket_query = models.ManyToManyField(PocketQuery, blank=True)
    point_type = models.CharField(max_length=64, choices=GPX_CHOICES)
    gpx_type = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    urlname = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(null=True)
    sym = models.CharField(max_length=100, blank=True, null=True)
    placed_by = models.CharField(max_length=100, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    long_description = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.FloatField(null=True)
    terrain = models.FloatField(null=True)
    container = models.CharField(max_length=100, blank=True, null=True)
    hints = models.TextField(blank=True, null=True)

    def __str__(self):

        return '%s - %s' % (self.name, self.urlname)
