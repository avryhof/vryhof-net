# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import AuthorizedAgent


@admin.register(AuthorizedAgent)
class AuthorizedAgentAdmin(admin.ModelAdmin):
    list_display = ("app_name", "user", "authorized")
    list_filter = ("authorized", "user")
