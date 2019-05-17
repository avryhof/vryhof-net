import random

from django.core.management import BaseCommand

from alexa.models import BedtimeStory
from alexa.skills import get_story


class Command(BaseCommand):
    help = 'Update weather station data from the Ambient Weather API.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        story_title = 'going to bed book'
        print(get_story(story_title=story_title))
