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
            news_item.abstract = multi_clean(news_item.abstract)

            if news_item.content:
                news_item.content = multi_clean(news_item.content)
            if news_item.guid:
                news_item.guid = multi_clean(news_item.guid)

            news_item.link = multi_clean(news_item.link)
            news_item.save()
