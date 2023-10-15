from django.contrib import admin

from custom_admin.utility_functions import is_empty


class EmptyFilter(admin.SimpleListFilter):
    title = "Has Value"
    parameter_name = "has_value"
    field_name = "field"

    def lookups(self, request, model_admin):
        return (
            ("not_empty", "Not Empty"),
            ("empty", "Empty"),
        )

    def queryset(self, request, queryset):
        if self.value() == "empty":
            keys = [item.pk for item in queryset if is_empty(getattr(item, self.field_name))]
            return queryset.filter(pk__in=keys)
        elif self.value() == "not_empty":
            keys = [item.pk for item in queryset if not is_empty(getattr(item, self.field_name))]
            return queryset.filter(pk__in=keys)

        return queryset
