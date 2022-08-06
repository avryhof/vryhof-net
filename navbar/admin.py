# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import NavbarLink, NavbarMenu


@admin.register(NavbarLink)
class NavbarLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "link_target", "active", "order")
    list_filter = ("active", "submenu")
    list_editable = ("order",)


@admin.register(NavbarMenu)
class NavbarMenuAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "active", "root_menu")
    list_filter = ("active", "root_menu")
    search_fields = ("name",)
    filter_horizontal = ("menu_items",)
