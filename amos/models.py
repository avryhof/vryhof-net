from ckeditor.fields import RichTextField
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from utilities.utility_functions import is_empty


class CVPage(models.Model):
    enabled = models.BooleanField(default=True)
    home = models.BooleanField(default=False)
    site = models.ForeignKey("sites.Site", on_delete=models.CASCADE)
    url_name = models.CharField(max_length=256, blank=True, null=True)
    django_page = models.BooleanField(default=False)
    page_url = models.CharField(max_length=256, blank=True, null=True)
    page_title = models.CharField(max_length=256, blank=True, null=True)
    template = models.CharField(max_length=256, blank=True, null=True, default="card-page.html",
                                choices=(("card-page.html", "Page"), ("card-home.html", "Home Page")))
    icon = models.CharField(
        max_length=256,
        default="fa-solid fa-",
        help_text=mark_safe(
            "Font Awesome icon from " '<a href="https://fontawesome.com/search?o=r&m=free" target="_blank">here</a>.'
        ),
    )
    authenticated = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.page_title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if is_empty(self.url_name):
            self.url_name = slugify(self.page_title)

        if not is_empty(self.url_name):
            if self.django_page:
                try:
                    self.page_url = reverse(self.url_name)
                except NoReverseMatch:
                    self.page_url = "/amos/page/{}/".format(self.url_name)
            else:
                try:
                    self.page_url = reverse("cv-page", kwargs={"page_slug": self.url_name})
                except NoReverseMatch:
                    if self.url_name.lower()[0:4] == "http":
                        self.page_url = self.url_name
                    elif self.url_name[0] == "/":
                        self.page_url = self.url_name
                    else:
                        self.page_url = "/amos/page/{}/".format(self.url_name)

        super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = ["order"]

    @property
    def content_blocks(self):
        return CVPageContent.objects.filter(page=self).order_by("order")

    @property
    def tool_html(self):
        return (
            f'<a href="{self.page_url}" class="cv-tool">'
            f'<div class="cv-tool-icon"><i class="{self.icon}"></i></div>'
            f'<div class="tool-label">{self.page_title}</div>'
            "</a>"
        )


class CVPageContent(models.Model):
    page = models.ForeignKey(CVPage, on_delete=models.CASCADE)
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
