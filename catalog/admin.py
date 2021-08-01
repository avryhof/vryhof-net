# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Catalog, CatalogItem, CatalogVariant, Location, LocationHours, LocationCapability


@admin.register(Catalog)
class CatalogAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class ItemVariantInline(admin.TabularInline):
    model = CatalogVariant
    fk_name = "catalog_item"
    fields = (
        "name",
        "price",
    )


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "catalog",
    )
    list_filter = ("catalog",)
    search_fields = ("name",)
    inlines = (ItemVariantInline,)


@admin.register(CatalogVariant)
class CatalogVariantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "catalog_item",
    )
    list_filter = ("catalog_item",)
    search_fields = ("name", "catalog_item")


class LocationHoursInline(admin.TabularInline):
    model = LocationHours
    fk_name = "location"
    fields = (
        "location",
        "day_of_week",
        "start_local_time",
        "end_local_time",
    )


class LocationCapabilityInline(admin.TabularInline):
    model = LocationCapability
    fk_name = "location"
    fields = ("capability",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address1",
        "city",
        "state",
        "zip_code",
        "location_status",
        "location_type",
        "business_name",
    )
    list_filter = ("zip_code", "validated", "created_at")
    search_fields = ("name",)
    date_hierarchy = "created_at"
    inlines = (
        LocationCapabilityInline,
        LocationHoursInline,
    )
