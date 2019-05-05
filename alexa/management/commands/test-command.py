import random

from django.core.management import BaseCommand

from alexa.models import BedtimeStory


class Command(BaseCommand):
    help = 'Update weather station data from the Ambient Weather API.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        all_stories = set(BedtimeStory.objects.filter(enabled=True))

        random_stories = random.sample(all_stories, 1)
        random_story = random.choice(random_stories)

        speech_text = random_story.story

        print(speech_text)
