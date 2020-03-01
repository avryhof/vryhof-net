# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import KidSite


@admin.register(KidSite)
class KidSiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'enabled', 'name', 'url', 'icon')
    list_filter = ('enabled',)
    search_fields = ('name',)
    list_editable = ["enabled"]