# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import PostalCode


@admin.register(PostalCode)
class PostalCodeAdmin(admin.ModelAdmin):
    list_display = (
        'country_code',
        'postal_code',
        'place_name',
        'admin_name1',
        'admin_code1',
        'admin_name2',
        'admin_code2',
        'admin_name3',
        'admin_code3',
        'latitude',
        'longitude',
        'accuracy',
    )
    list_filter = ('admin_name1', 'admin_code1',)
    search_fields = ("place_name", 'admin_name1', 'admin_code1', 'admin_name2',)
