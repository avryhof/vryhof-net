import requests
import uuid0
from django.core.management import BaseCommand
from django.urls import reverse

from utilities.debugging import log_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        rfid_id = str(uuid0.generate())
        endpoint_path = reverse("rfid-lookup")

        endpoint_url = "http://127.0.0.1:8000{}".format(endpoint_path)
        # endpoint_url = "https://firefox.vryhof.net{}".format(endpoint_path)

        log_message("talking to: {}".format(endpoint_url))

        resp = requests.post(endpoint_url, data=dict(catalog_id=1, rfid_id=rfid_id))

        print(resp.text)
