from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from content.models import PageContent, Page, SidebarItem
from utilities.utility_functions import is_empty


class PageContentInline(admin.StackedInline):
    fk_name = "page"
    model = PageContent
    fields = ("html_content",)
    show_change_link = True
    can_delete = False
    extra = 0


@admin.action(description="Clone")
def clone_page(modeladmin, request, queryset):
    for obj in queryset:
        obj.__class__.objects.create(
            site=obj.site,
            url_name=obj.url_name,
            page_url=obj.page_url,
            page_title=obj.page_title,
        )


@admin.action(description="Create Sidebar Item")
def page_to_sidebar_item(modeladmin, request, queryset):
    si = SidebarItem.objects.all().order_by("order").last()
    if not is_empty(si):
        order = si.order
    else:
        order = 0

    for obj in queryset:
        order = order + 1
        SidebarItem.objects.create(page=obj, order=order)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = [
        "page_title",
        "site",
        "url_name",
        "page_url",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "page_title",
                    "site",
                    (
                        "url_name",
                        "page_url",
                    ),
                ]
            },
        ),
    ]
    readonly_fields = ["page_url"]
    inlines = [PageContentInline]
    actions = [clone_page, ]


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ["page", "order"]
    fieldsets = [
        (
            None,
            {"fields": ["page", "order"]},
        ),
        (_("Content"), {"fields": ["html_content", "code_content"]}),
    ]
    list_editable = ["order"]
    list_filter = ["page"]


@admin.action(description="Clone")
def clone_sidebar_item(modeladmin, request, queryset):
    for obj in queryset:
        obj.__class__.objects.create(
            page=obj.page,
            icon=obj.icon,
            authenticated=obj.authenticated,
            order=obj.order + 1,
        )


@admin.register(SidebarItem)
class SidebarItemAdmin(admin.ModelAdmin):
    list_display = ["page", "icon", "authenticated", "order"]
    fields = ["page", "icon", "authenticated", "order"]
    list_editable = ["order"]
    actions = [clone_sidebar_item]
