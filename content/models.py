from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from utilities.utility_functions import is_empty


class Page(models.Model):
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE)
    url_name = models.CharField(max_length=256, blank=True, null=True)
    page_url = models.CharField(max_length=256, blank=True, null=True)
    page_title = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.page_title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if is_empty(self.url_name):
            self.url_name = slugify(self.page_title)

        if not is_empty(self.url_name):
            try:
                self.page_url = reverse(self.url_name)
            except NoReverseMatch:
                if "http" in self.url_name:
                    self.page_url = self.url_name
                else:
                    self.page_url = "/page/{}/".format(self.url_name)

        super().save(force_insert, force_update, using, update_fields)

    @property
    def content_blocks(self):
        return PageContent.objects.filter(page=self).order_by("order")


class PageContent(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    html_content = RichTextField()
    code_content = models.TextField()

    class Meta:
        ordering = ["page", "order"]

    @property
    def content(self):
        if not is_empty(self.code_content):
            return self.code_content

        return self.html_content


class SidebarItem(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    icon = models.CharField(
        max_length=256,
        default="fa-solid fa-",
        help_text=mark_safe(
            "Font Awesome icon from "
            '<a href="https://fontawesome.com/search?o=r&m=free" target="_blank">here</a>.'
        ),
    )
    authenticated = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    @property
    def html(self):
        return (
            '<div class="sidebar-item">'
            f'<a href="{self.page.page_url}">'
            f'<div class="icon"><i class="{self.icon} fa-2x"></i></div>'
            f'<div class="label">{self.page.page_title}</div>'
            "</a></div>"
        )
