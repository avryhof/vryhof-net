# -*- coding: utf-8 -*-
from django.contrib import admin

from geocaching.utility_functions import camel_to_words, process_pocket_query
from .models import GPXFile, PocketQuery, Point


@admin.register(GPXFile)
class GPXFileAdmin(admin.ModelAdmin):
    list_display = ("gpx_file", "file_type", "Last Updated", "updated_by")
    list_filter = ("gpx_file", "Last Updated", "updated_by")

    def delete_model(self, request, obj):
        obj.gpx_file.delete()


@admin.register(PocketQuery)
class PocketQueryAdmin(admin.ModelAdmin):
    list_display = ("name", "Last Updated", "updated_by")
    list_filter = ("geocaches", "waypoints", "Last Updated", "updated_by")
    search_fields = ("name",)

    def save_model(self, request, obj, form, change):
        filename = obj.zip_file.original_filename

        if not obj.updated_by:
            obj.updated_by = request.user

        if not obj.name:
            obj.name = camel_to_words(filename.split(".")[0].split("_")[1])

        obj.save()

        process_pocket_query(obj)


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ("name", "urlname", "point_type", "latitude", "longitude", "country", "state")
    list_filter = ("time", "point_type", "gpx_type", "container", "difficulty", "terrain")
    search_fields = ("name",)
