# -*- coding: utf-8 -*-
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import WeatherStation, WeatherData


class WeatherStationResource(resources.ModelResource):
    class Meta:
        model = WeatherStation


@admin.register(WeatherStation)
class WeatherStationAdmin(ImportExportModelAdmin):
    list_display = ("name", "location", "mac_address", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name",)


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ("station", "date", "tempf")
    list_filter = ("station", "date")
