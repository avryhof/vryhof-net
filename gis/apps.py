import os

from django.apps import AppConfig
from django.conf import settings


class GisConfig(AppConfig):
    name = 'gis'
    path = os.path.join(settings.BASE_DIR, "gis")
