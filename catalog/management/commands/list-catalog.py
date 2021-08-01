from django.core.management import BaseCommand

from catalog.models import Catalog
from catalog.square_base import square_client
from utilities.debugging import log_message


class Command(BaseCommand):
    def handle(self, *args, **options):
        for catalog in Catalog.objects.all():
            data = catalog.list()

            log_message(data, pretty=True)
