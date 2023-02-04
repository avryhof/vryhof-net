# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "city",
        "state",
        "zip_code",
        "user",
    )
    list_filter = (
        "city",
        "state",
        "zip_code",
    )
    readonly_fields = ("display_name",)
    search_fields = (
        "first_name",
        "last_name",
        "prefix",
        "suffix",
        "zip_code",
        "city",
    )
