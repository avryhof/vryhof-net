# -*- coding: utf-8 -*-
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from navbar.models import NavbarLink, NavbarMenu


class NavbarLinkResource(resources.ModelResource):
    class Meta:
        model = NavbarLink


class NavbarMenuResource(resources.ModelResource):
    class Meta:
        model = NavbarMenu


@admin.register(NavbarLink)
class NavbarLinkAdmin(ImportExportModelAdmin):
    resource_class = NavbarLinkResource
    list_display = ("title", "link_target", "active", "order")
    list_filter = ("active", "submenu")
    list_editable = ("order",)


@admin.register(NavbarMenu)
class NavbarMenuAdmin(ImportExportModelAdmin):
    resource_class = NavbarMenuResource
    list_display = ("name", "order", "active", "root_menu")
    list_filter = ("active", "root_menu")
    search_fields = ("name",)
    filter_horizontal = ("menu_items",)
