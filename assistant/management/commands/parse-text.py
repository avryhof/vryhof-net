import pytz
import datetime
import json
import os

import requests
from django.conf import settings
from django.core.management import BaseCommand
from django.urls import reverse

from assistant.models import AuthorizedAgent


class Command(BaseCommand):
    help = 'Send the Skill initiation code to the Alexa Skill on the server.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        naive_date = datetime.datetime.now()
        localtz = pytz.timezone('America/New_York')
        date_aware = localtz.localize(naive_date)

        auth = AuthorizedAgent.objects.get(authorized=True)

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'ASSISTANT-AGENT': '%s' % auth.app_key
        },

        data = {
            'text': 'Hello World',
            'timestamp': date_aware.isoformat()
        }

        endpoint = 'http://127.0.0.1:8000'
        request_url = '%s%s' % (endpoint, reverse('parse_text'))

        # ret = requests.post('https://alexa.vryhof.net/alexa/', json=json_to_send)
        ret = requests.post(request_url, json=json.dumps(data), headers=headers)

        print(ret.text)


