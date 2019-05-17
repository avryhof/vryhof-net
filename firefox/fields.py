from django import forms
from django.core import validators
from django.db.models import TextField
from django.utils.translation import gettext_lazy as _


class LongURLField(TextField):
    default_validators = [validators.URLValidator()]
    description = _("URL")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        return super().formfield(**{"form_class": forms.URLField, **kwargs})
