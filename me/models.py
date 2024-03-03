from adminsortable.models import SortableMixin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.safestring import mark_safe

from gis.models import AbstractStreetAddress
from me.helpers import photo_upload_path
from utilities.utility_functions import is_empty


class Member(AbstractStreetAddress):
    user = models.ForeignKey(get_user_model(), blank=True, null=True, on_delete=models.SET_NULL)
    prefix = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    work = models.CharField(max_length=20, blank=True, null=True)
    cell = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    email_me = models.BooleanField(default=True)
    call_me = models.BooleanField(default=True)
    photo = models.ImageField(blank=True, null=True, upload_to=photo_upload_path)

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        return self.display_name

    def save(self, *args, **kwargs):
        if self.name is None:
            name_parts = [self.prefix, self.first_name, self.middle_name, self.last_name, self.suffix]
            self.name = " ".join([part for part in name_parts if isinstance(part, str)])

        return super().save(*args, **kwargs)

    @property
    def display_name(self):
        if self.name is None:
            name_parts = [self.prefix, self.first_name, self.middle_name, self.last_name, self.suffix]
            self.name = " ".join([part for part in name_parts if part is not None])
            self.save()
        return self.name

    @property
    def email_address(self):
        return mark_safe(
            '<a href="mailto:{}">{}</a>'.format(
                self.user.email if not is_empty(self.user) else self.email,
                self.user.email if not is_empty(self.user) else self.email,
            )
        )

    @property
    def html_address(self):
        address_str = "<br>".join([a for a in [self.address1, self.address2] if not is_empty(a)])
        if not is_empty(self.plus_four):
            return mark_safe(
                "<address>{}<br>{}, {} {}-{}".format(address_str, self.city, self.state, self.zip_code, self.plus_four)
            )
        else:
            return mark_safe("<address>{}<br>{}, {} {}".format(address_str, self.city, self.state, self.zip_code))
