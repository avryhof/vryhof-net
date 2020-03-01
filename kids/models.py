from django.db.models import Model, CharField, URLField, BooleanField, FileField


class KidSite(Model):
    enabled = BooleanField()
    name = CharField(max_length=30, blank=True, null=True)
    url = URLField(null=True)
    icon = FileField(null=True)
