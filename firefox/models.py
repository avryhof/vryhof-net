from django.db.models import Model, CharField, BooleanField, URLField, TextField, ForeignKey, DateTimeField, DO_NOTHING


class NewsFeed(Model):
    active = BooleanField(default=True)
    title = CharField(max_length=255, blank=True, null=True)
    url = URLField(blank=True, null=True)

    def __str__(self):
        retn = 'NewsFeed %i' % self.pk

        if self.title:
            retn = self.title
        elif self.url:
            retn = self.url

        return retn


class NewsImage(Model):
    url = URLField(blank=True, null=True)
    guid = CharField(max_length=128, blank=True, null=True)


class NewsItem(Model):
    title = CharField(max_length=255)
    poster = ForeignKey(NewsImage, blank=True, on_delete=DO_NOTHING)
    abstract = TextField(blank=True, null=True)
    link = URLField(blank=True, null=True)
    comments = URLField(blank=True, null=True)
    guid = TextField(blank=True, null=True)
    date = DateTimeField(blank=True, null=True)
