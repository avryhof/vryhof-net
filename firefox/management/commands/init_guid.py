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
            news_item.guid = news_item.link
            news_item.save()

        for news_item in news_items:
            dupes = NewsItem.objects.filter(guid=news_item.guid).order_by('-pk')

            article = 1
            for dupe in dupes:
                if article > 1:
                    dupe.delete()

                article += 1
