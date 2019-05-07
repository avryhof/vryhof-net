import pytz
import datetime
import json
import os

import requests
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Send the Skill initiation code to the Alexa Skill on the server.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        json_file = os.path.join(settings.BASE_DIR, 'alexa', 'json', 'test-load.json')
        js = open(json_file)

        if os.path.exists(json_file):
            json_to_send = json.load(js)

            naive_date = datetime.datetime.now()
            localtz = pytz.timezone('America/New_York')
            date_aware = localtz.localize(naive_date)

            json_to_send['request']['timestamp'] = date_aware.isoformat()

            ret = requests.post('https://alexa.vryhof.net/alexa/', json=json_to_send)
            # ret = requests.post('http://127.0.0.1:8000/alexa/', json=json_to_send)

            print(ret)
            print(ret.text)


