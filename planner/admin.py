# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import EventType, Event, MealType, Meal


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "default_start_time", "default_end_time")
    search_fields = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "start_time", "end_time", "event_type")
    list_filter = ("start_time", "end_time", "event_type")


@admin.register(MealType)
class MealTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "default_start_time", "default_end_time")
    search_fields = ("name",)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "start_time", "end_time", "meal")
    list_filter = ("start_time", "end_time", "meal")
