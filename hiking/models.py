from django.db.models import URLField, Model, ForeignKey, DO_NOTHING, CharField

from gis.models import GISPoint
from web_discover.models import WebPath


class HikeSource(Model):
    name = CharField(max_length=255, blank=True, null=True)
    url = URLField(blank=True, null=True)

    @property
    def html(self):
        return self.webpath.html

    @property
    def webpath(self):
        try:
            web_path = WebPath.objects.get(url=self.url)
        except WebPath.DoesNotExist:
            web_path = WebPath.objects.create(url=self.url)
            web_path.save()

        return web_path


class Hike(GISPoint):
    url = URLField(blank=True, null=True)

    @property
    def html(self):
        return self.webpath.html

    @property
    def webpath(self):
        try:
            web_path = WebPath.objects.get(url=self.url)
        except WebPath.DoesNotExist:
            web_path = WebPath.objects.create(url=self.url)
            web_path.save()

        return web_path


class HikeImage(Model):
    hike = ForeignKey(Hike, blank=True, null=True, on_delete=DO_NOTHING)
