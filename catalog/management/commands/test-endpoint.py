import requests
import uuid0
from django.core.management import BaseCommand
from django.urls import reverse


class Command(BaseCommand):
    def handle(self, *args, **options):
        rfid_id = str(uuid0.generate())
        endpoint_path = reverse("rfid-lookup")

        endpoint_url = "http://127.0.0.1:8000{}".format(endpoint_path)

        resp = requests.post(endpoint_url, data=dict(rfid_id=rfid_id))

        print(resp.text)
