from django.core.exceptions import ImproperlyConfigured
from django.utils.safestring import mark_safe

from custom_admin.utility_functions import make_list, is_empty
from custom_admin.utils import admin_change_link


class AdminInlineQueryset:
    appname = None
    model = None
    model_name = ""
    queryset = []
    fields = []
    list_display_links = []

    def __init__(self, qs, **kwargs):
        # self.appname =
        self.queryset = qs
        self.model = self.queryset.model_name
        self.model_name = self.model.__name__
        self.fields = self.model._meta.get_fields()
        self.appname = self.model._meta.app_label

        if "fields" in kwargs:
            self.fields = make_list(kwargs.get("fields"))

        if "list_display_links" in kwargs:
            self.list_display_links = make_list(kwargs.get("list_display_links"))

        if is_empty(self.fields):
            raise ImproperlyConfigured("fields must be specified")

        if is_empty(self.list_display_links):
            self.list_display_links = self.fields

    def get_field(self, field, attr):
        if hasattr(field, "__dict__"):
            field_dict = getattr(field, "__dict__")
            return field_dict.get(attr)

        elif isinstance(field, str):
            print(field)

        return False

    def get_field_header(self):
        header_names = []
        for field in self.fields:
            if isinstance(field, str):
                header_name = " ".join(field.split("_")).title()
            else:
                header_name = self.get_field(field, "verbose_name")

            header_names.append(str(header_name))

        return "<tr><th>{}</th></tr>".format("</th><th>".join(header_names))

    def get_field_data(self, item):
        return_data = []

        admin_link = admin_change_link(self.appname, self.model_name, item)
        for field in self.fields:
            value = False
            if isinstance(field, str):
                value = getattr(item, field)
            else:
                field_name = self.get_field(field, "name")
                if not is_empty(field_name):
                    if isinstance(field_name, str):
                        value = getattr(item, field_name)

            if not is_empty(value):
                if field in self.list_display_links:
                    return_data.append('<a href="{}">{}</a>'.format(admin_link, value))
                else:
                    return_data.append(value)

        return "<tr><td>{}</td></tr>".format("</td><td>".join(return_data))

    @property
    def html(self):
        tbody_items = ["<tr>{}</tr>".format(self.get_field_data(query_item)) for query_item in self.queryset]
        return mark_safe(
            "<table><thead>{}</thead><tbody>{}</tbody></table>".format(self.get_field_header(), "".join(tbody_items))
        )


class AdminJSONInline:
    json_data = {}
    fields = []

    def __init__(self, json_field, **kwargs):
        self.json_data = json_field
        self.fields = dict(json_field).keys()

        if "fields" in kwargs:
            self.fields = make_list(kwargs.get("fields"))

        if is_empty(self.fields):
            raise ImproperlyConfigured("fields must be specified")

    def get_field_header(self):
        header_names = []
        for field in self.fields:
            header_name = " ".join(field.split("_")).title()
            header_names.append(str(header_name))

        return "<tr><th>{}</th></tr>".format("</th><th>".join(header_names))

    def get_field_data(self, item):
        return_data = []

        for field in self.fields:
            value = item.get(field)

            if not is_empty(value):
                return_data.append(value)

        return "<tr><td>{}</td></tr>".format("</td><td>".join(return_data))

    @property
    def html(self):
        tbody_items = ["<tr>{}</tr>".format(self.get_field_data(field_value)) for field_value in self.fields]
        return mark_safe(
            "<table><thead>{}</thead><tbody>{}</tbody></table>".format(self.get_field_header(), "".join(tbody_items))
        )
