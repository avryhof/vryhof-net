# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Intent, LanguageModel, BedtimeStory


@admin.register(Intent)
class IntentAdmin(admin.ModelAdmin):
    list_display = ("name", "enabled")
    list_filter = ("enabled",)
    search_fields = ("name",)


@admin.register(LanguageModel)
class LanguageModelAdmin(admin.ModelAdmin):
    list_display = ("invocation_name", "enabled")
    list_filter = ("enabled",)
    filter_horizontal = ("intents",)


@admin.register(BedtimeStory)
class BedtimeStoriesAdmin(admin.ModelAdmin):
    list_display = ("title", "enabled")
    list_filter = ("enabled",)
