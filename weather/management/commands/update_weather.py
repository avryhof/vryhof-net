from django.core.management import BaseCommand

from weather.utilities import get_weather


class Command(BaseCommand):
    help = "Update weather station data from the Ambient Weather API."
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options["verbosity"])

        get_weather()
