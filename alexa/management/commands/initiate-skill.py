import pprint
from json import JSONDecodeError

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

        json_file = os.path.join(settings.BASE_DIR, 'alexa', 'json', 'test-load.json')
        js = open(json_file)

        if os.path.exists(json_file):
            json_to_send = json.load(js)

            naive_date = datetime.datetime.now()
            localtz = pytz.timezone('America/New_York')
            date_aware = localtz.localize(naive_date)

            json_to_send['request']['timestamp'] = date_aware.isoformat()

            auth = AuthorizedAgent.objects.get(authorized=True)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'ASSISTANT-AGENT': '%s' % auth.app_key
            }

            endpoint = 'http://127.0.0.1:8000'
            request_url = '%s%s' % (endpoint, reverse('intent'))
            # request_url = '%s%s' % (endpoint, reverse('index'))

            # ret = requests.post('https://alexa.vryhof.net/alexa/', json=json_to_send)
            # ret = requests.post(request_url, json=json_to_send)
            ret = requests.post(request_url, json=json_to_send, headers=headers)

            print(ret)

            try:
                pprint.pprint(ret.json())

            except JSONDecodeError:
                print(ret.text)


