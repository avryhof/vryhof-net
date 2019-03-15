from django.core.management import BaseCommand

from firefox.models import NewsItem
from firefox.utilities import multi_clean


class Command(BaseCommand):
    help = 'Clean up iframes from abstracts.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        news_items = NewsItem.objects.all()

        for news_item in news_items:
            guid = news_item.guid

            if not guid:
                news_item.guid = multi_clean(news_item.link)
                news_item.save()
