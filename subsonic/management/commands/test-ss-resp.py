import requests
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        resp = requests.get("http://127.0.0.1:8000/subsonic/stream/18739/")
        print(resp.headers)
