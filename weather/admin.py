# -*- coding: utf-8 -*-
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import WeatherStation, WeatherData, NWSPoint, NWSForecast, WeatherImages


class WeatherStationResource(resources.ModelResource):
    class Meta:
        model = WeatherStation


class NWSPointResource(resources.ModelResource):
    class Meta:
        model = NWSPoint


@admin.register(WeatherStation)
class WeatherStationAdmin(ImportExportModelAdmin):
    list_display = ("name", "location", "mac_address", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name",)


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ("station", "date", "tempf")
    list_filter = ("station", "date")


@admin.register(WeatherImages)
class WeatherImagesAdmin(admin.ModelAdmin):
    list_display = ("date", "time" "filename")


@admin.register(NWSPoint)
class NWSPointAdmin(ImportExportModelAdmin):
    list_display = ("grid_id", "grid_x", "grid_y", "radar_station")
    list_filter = ("grid_x", "grid_y")


@admin.register(NWSForecast)
class NWSForecastAdmin(admin.ModelAdmin):
    list_display = (
        "day_name",
        "day_number",
        "start_time",
        "end_time",
    )
