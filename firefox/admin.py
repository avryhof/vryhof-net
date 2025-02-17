# -*- coding: utf-8 -*-
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from firefox.models import NewsFeed, NewsImage, NewsItem


class NewsFeedResource(resources.ModelResource):
    class Meta:
        model = NewsFeed


@admin.register(NewsFeed)
class NewsFeedAdmin(ImportExportModelAdmin):
    resource_class = NewsFeedResource
    list_display = ("title", "active", "url")
    list_filter = ("active",)


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ("url",)


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "feed")
    list_filter = ("date",)
