import datetime

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand

from firefox.models import NewsItem
from firefox.utilities import get_feeds


class Command(BaseCommand):
    help = 'Pull data from news feeds, and clean up news older than two weeks.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        get_feeds()

        two_weeks_ago = datetime.datetime.now() - relativedelta(weeks=2)

        NewsItem.objects.filter(date__lt=two_weeks_ago).delete()

