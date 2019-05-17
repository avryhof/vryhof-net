# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import NewsFeed, NewsImage, NewsItem


@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ("title", "active", "url")
    list_filter = ("active",)


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ("url",)


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "date", "feed")
    list_filter = ("date",)
