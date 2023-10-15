from django.contrib import admin

from custom_admin.models import ExceptionLog


@admin.register(ExceptionLog)
class ExceptionLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "path")
    fields = (
        "timestamp",
        "troubleshooter_link",
        "path",
        "filename",
        "function_name",
        "line_number",
        "message",
        "exception",
        "formatted_traceback",
    )
    readonly_fields = (
        "timestamp",
        "troubleshooter_link",
        "path",
        "filename",
        "function_name",
        "line_number",
        "exception",
        "formatted_traceback",
    )
    list_filter = ("path", "function_name", "filename")
    search_fields = ("user__username", "user__email", "exception", "function_name")
