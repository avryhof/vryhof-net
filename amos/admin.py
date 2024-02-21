from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from amos.models import CVPageContent, CVPage


class CVPageContentInline(admin.StackedInline):
    fk_name = "page"
    model = CVPageContent
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


@admin.register(CVPage)
class PageAdmin(admin.ModelAdmin):
    list_display = ["page_title", "site", "url_name", "page_url", "enabled", "order"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "page_title",
                    "site",
                    ("enabled", "home"),
                    (
                        "url_name",
                        "django_page",
                        "page_url",
                    ),
                    "template",
                ]
            },
        ),
        (_("Sidebar Item"), {"fields": ["icon", "authenticated", "order"]}),
    ]
    list_filter = ["site", "enabled", "authenticated"]
    readonly_fields = ["page_url"]
    inlines = [CVPageContentInline]
    actions = [clone_page]


@admin.register(CVPageContent)
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
