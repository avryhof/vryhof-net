# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import WeatherStation, WeatherData


@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'mac_address', 'enabled')
    list_filter = ('enabled',)
    search_fields = ('name',)


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = (
        'station',
        'date',
        'tempf',
    )
    list_filter = ('station', 'date',)
