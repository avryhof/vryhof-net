import pprint

from api.wikipedia import Wikipedia
from gis.models import PostalCode
from utilities.command_baseclass import ManagementCommand


class Command(ManagementCommand):
    def handle(self, *args, **options):
        w = Wikipedia()

        try:
            postal_code = PostalCode.objects.get(postal_code="13212")
        except PostalCode.DoesNotExist:
            pass
        else:
            pprint.pprint(w.get_by_coordinates(postal_code.latitude, postal_code.longitude))
