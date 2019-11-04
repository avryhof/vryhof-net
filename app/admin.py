# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Point


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
        "address1",
        "address2",
        "city",
        "state",
        "zip_code",
        "plus_four",
        "postal_code",
        "validated",
        "time",
    )
    list_filter = ("state",)
    search_fields = ("name",)
    readonly_fields = ("postal_code", "validated", "time")
