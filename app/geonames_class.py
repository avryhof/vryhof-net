import datetime
import json
import logging
import os
import pprint

import requests
from future.standard_library import install_aliases

from gis.data_functions import convert_keys

install_aliases()

logger = logging.getLogger(__name__)


class GeoNames:
    is_debug = False
    is_logging = False

    today = None

    username = None
    endpoint = "http://api.geonames.org"

    def __init__(self, **kwargs):
        self.is_debug = kwargs.get("debug", os.environ.get("FED_DEBUG", False)) in ["True", True]
        self.is_logging = kwargs.get("logging", os.environ.get("FED_LOGGING", False)) in ["True", True]

        self.username = kwargs.get("username", "demo")

        self.today = datetime.datetime.now()

    def debug_msg(self, message, **kwargs):
        pretty = kwargs.get("pretty", False)

        if pretty:
            message = pprint.pformat(message, indent=4)

        if self.is_debug:
            print(message)

        if self.is_logging:
            logger.info(message)

    def reverse_geocode(self, **kwargs):
        return_address = dict()

        searchtype = kwargs.get("searchtype", "extendedFindNearby")
        returntype = kwargs.get("format", "JSON")

        params_dict = dict(username=self.username)
        query = kwargs.get("query", False)

        if query:
            if "lat" not in query and "latitude" in query:
                query["lat"] = query.get("latitude")
                del query["latitude"]

            if "lng" not in query and "longitude" in query:
                query["lng"] = query.get("longitude")
                del query["longitude"]

            params_dict += query

        if not query and "lat" in kwargs or "latitude" in kwargs:
            params_dict.update(
                dict(
                    lat=kwargs.get("lat", kwargs.get("latitude", None)),
                    lng=kwargs.get("lng", kwargs.get("longitude", None)),
                )
            )

        self.debug_msg("Performing a %s search, and receiving results in %s format." % (searchtype, returntype))

        if isinstance(params_dict, dict):
            nearby_url_base = "%s/%s%s" % (self.endpoint, searchtype, returntype)
            self.debug_msg("URL: %s" % nearby_url_base)
            self.debug_msg("Parameters: %s" % params_dict)

            self.debug_msg("Sending GET request.")
            nearby_resp = requests.get(nearby_url_base, params=params_dict)
            self.debug_msg("Request complete.")

            if nearby_resp.status_code == 200:
                if "address" in nearby_resp.json():
                    return_address.update(dict(nearby=nearby_resp.json().get("address")))
            else:
                self.debug_msg("Something went wrong: %s: %s" % (nearby_resp.status_code, nearby_resp.text))

        return return_address
