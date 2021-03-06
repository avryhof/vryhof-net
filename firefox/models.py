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
