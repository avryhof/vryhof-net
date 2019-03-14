import re
from django.core.management import BaseCommand

from firefox.models import NewsItem


class Command(BaseCommand):
    help = 'Clean up iframes from abstracts.'
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    def handle(self, *args, **options):
        self.verbosity = int(options['verbosity'])

        news_items = NewsItem.objects.filter(abstract__icontains='iframe')

        for news_item in news_items:
            abstract = news_item.abstract
            news_item.abstract = re.sub('\<iframe.*?iframe\>', '', abstract)
            news_item.abstract = news_item.abstract.replace('http:', 'https:')
            news_item.save()

