from bs4 import BeautifulSoup
from django.db.models import (
    Model,
    CharField,
    BooleanField,
    URLField,
    TextField,
    ForeignKey,
    DateTimeField,
    DO_NOTHING,
)

from firefox.fields import LongURLField
from utilities.utility_functions import is_empty


class NewsFeed(Model):
    active = BooleanField(default=True)
    title = CharField(max_length=255, blank=True, null=True)
    url = LongURLField(blank=True, null=True)
    link = LongURLField(blank=True, null=True)
    description = TextField(blank=True, null=True)

    def __str__(self):
        retn = "NewsFeed %i" % self.pk

        if self.title:
            retn = self.title
        elif self.url:
            retn = self.url

        return retn


class NewsImage(Model):
    url = URLField(blank=True, null=True)
    guid = CharField(max_length=128, blank=True, null=True)


class NewsItem(Model):
    feed = ForeignKey(NewsFeed, blank=True, null=True, on_delete=DO_NOTHING)
    title = CharField(max_length=255)
    poster = ForeignKey(NewsImage, blank=True, null=True, on_delete=DO_NOTHING)
    abstract = TextField(blank=True, null=True)
    content = TextField(blank=True, null=True)
    link = LongURLField(blank=True, null=True)
    comments = LongURLField(blank=True, null=True)
    guid = TextField(blank=True, null=True)
    date = DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-date"]

    @property
    def cleaned_content(self):
        if not is_empty(self.content):
            content_html = self.content
        else:
            content_html = self.abstract

        soup = BeautifulSoup(content_html, "html.parser")
        images = soup.find_all("img")
        for image in images:
            content_html = content_html.replace(str(image), f'<img src="{image["src"]}">')

        return content_html
