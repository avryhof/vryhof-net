import pprint
from urllib.parse import quote

import requests

from api.wikipedia import Wikipedia
from gis.models import PostalCode
from utilities.api_utils import http_build_query
from utilities.command_baseclass import ManagementCommand


class Command(ManagementCommand):
    def handle(self, *args, **options):
        w = Wikipedia()

        try:
            postal_code = PostalCode.objects.get(postal_code="13212")
        except PostalCode.DoesNotExist:
            pass
        else:
            # pprint.pprint(w.get_by_coordinates(postal_code.latitude, postal_code.longitude))

            params = dict(
                action="query",
                format="json",
                list="geosearch",
                gscoord="{}|{}".format(round(postal_code.latitude, 7), round(postal_code.longitude, 7)),
                gsradius=10000,
                gslimit=100,
            )

            resp = requests.get("https://en.wikipedia.org/w/api.php", params=params)

            pprint.pprint(resp.json())
