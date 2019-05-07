import pytz
import datetime
import json
import os

import requests
from django.conf import settings
from django.core.management import BaseCommand

from weather.models import WeatherStation, WeatherData


class Command(BaseCommand):
    help = 'Send the Skill initiation code to the Alexa Skill on the server.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        station = WeatherStation.objects.get(name='KD2OTL')
        weather = WeatherData.objects.filter(station=station).order_by('-date')[0]

        speech_text = '%s says it is %s degrees fahrenheit as of %s on %s.' % (
            station.name,
            weather.tempinf,
            datetime.datetime.now().strftime('%I:%M %p'),
            datetime.datetime.now().strftime('%B %d, %Y')
        )

        print(speech_text)


