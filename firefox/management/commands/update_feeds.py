from django.core.management import BaseCommand

from firefox.utilities import get_feeds


class Command(BaseCommand):
    help = 'Update the controlled substance flag for all drugs based on the latest controlled substance list.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        get_feeds()
