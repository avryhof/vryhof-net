from django.conf import settings
from django.db import models
from django.db.models import DO_NOTHING, CASCADE
from filer.fields.file import FilerFileField

from gis.models import GISPoint, AbstractStreetAddress
from poi.constants import GPX_CHOICES
from utilities.excel import csv_to_dicts


class PointCategory(models.Model):
    name = models.CharField(max_length=120, blank=True, null=True)
    list_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class GPXFile(models.Model):
    gpx_file = FilerFileField(null=True, blank=True, on_delete=CASCADE)
    file_type = models.CharField(max_length=64, choices=GPX_CHOICES)
    updated_last_on = models.DateTimeField(auto_now=True, blank=True, editable=False, name="Last Updated")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True, on_delete=DO_NOTHING)

    def __str__(self):
        return self.gpx_file.original_filename


class PocketQuery(models.Model):
    name = models.CharField(max_length=250, blank=True, null=True)
    zip_file = FilerFileField(null=True, blank=True, on_delete=DO_NOTHING)
    geocaches = models.ForeignKey(GPXFile, blank=True, null=True, on_delete=DO_NOTHING, related_name="geocaches")
    waypoints = models.ForeignKey(GPXFile, blank=True, null=True, on_delete=DO_NOTHING, related_name="waypoints")
    updated_last_on = models.DateTimeField(auto_now=True, blank=True, editable=False, name="Last Updated")
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
        return "%s - %s" % (self.name, self.urlname)


class PlaceImport(models.Model):
    category = models.ForeignKey(PointCategory, blank=True, null=True, on_delete=models.SET_NULL)
    file = FilerFileField(null=True, blank=True, on_delete=CASCADE)
    imported = models.BooleanField(default=False)
    datestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     super().save(force_insert, force_update, using, update_fields)
    #
    #     if not self.imported:
    #         self.import_items()
    #         self.imported = True
    #         self.save()

    @property
    def data(self):
        return csv_to_dicts(self.file.path)

    def import_items(self):
        for item in self.data:
            name = item.get("title")
            url = item.get("URL")
            note = item.get("Note")
            comment = item.get("Comment")

            try:
                poi = PointOfInterest.objects.get(category=self.category, name=name)
            except PointOfInterest.DoesNotExist:
                poi = PointOfInterest.objects.create(
                    category=self.category, name=name, url=url, note=note, comment=comment
                )


class PointOfInterest(AbstractStreetAddress):
    category = models.ForeignKey(PointCategory, blank=True, null=True, on_delete=models.SET_NULL)
    url = models.URLField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
