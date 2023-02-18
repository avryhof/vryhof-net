import datetime
import os.path

import requests
from django.conf import settings
from geolite2utils import GeoLite2Utils

from gis.utility_functions import get_postal_code_by_coords, get_geoname_by_coords
from livechat.devices.weather.device import Weather
from livechat.personal_assistant.base_class import BaseClass
from livechat.utilities.timedate import AwareDateTime
from livechat.utilities.utility_functions import is_empty


class GeoIP(BaseClass):
    data_path = os.path.join(os.path.dirname(__file__), "data")
    db_path = None

    geolite2 = None
    client = None

    ip_address = None
    data = None

    latitude = None
    longitude = None
    geoname_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not is_empty(kwargs.get("data_path")):
            self.data_path = kwargs.get("data_path")

        if not os.path.exists(self.data_path):
            os.makedirs(self.data_path)

        self.data_file = os.path.join(self.data_path, "GeoLite2-City.mmdb")
        if not os.path.exists(self.data_file):
            self.update_db()

        self.geolite2 = GeoLite2Utils(getattr(settings, "GEOIP_KEY"), self.data_path)
        self.client = self.geolite2.reader(GeoLite2Utils.CITY)

    def update_db(self):
        # download the archive of the database; this might be hundreds of megabytes depending on the db
        self.geolite2.download(GeoLite2Utils.CITY)

        # extract the archive
        self.geolite2.extract(GeoLite2Utils.CITY)

        # clean up the .tar.gz archive so it doesn't waste disk space
        self.geolite2.cleanup(GeoLite2Utils.CITY)

    def get_location(self, ip_address=None):
        if is_empty(ip_address):
            req = requests.get("https://api.ipify.org/?format=text")
            self.ip_address = req.text
        else:
            self.ip_address = ip_address

        self.data = self.client.city(self.ip_address)
        self.latitude = self.data.location.latitude
        self.longitude = self.data.location.longitude
        self.geoname_id = self.data.city.geoname_id

    def get_local_time(self):
        return AwareDateTime(datetime.datetime.now(), self.time_zone)

    def get_weather(self):
        return Weather(self.latitude, self.longitude)

    @property
    def city(self):
        return self.data.city.name

    @property
    def state(self):
        return self.data.subdivisions[0].iso_code

    @property
    def state_name(self):
        return self.data.subdivisions[0].name

    @property
    def zip_code(self):
        return self.data.postal.code

    @property
    def time_zone(self):
        return self.data.location.time_zone

    @property
    def coordinates(self):
        return self.latitude, self.longitude


class Geoname(BaseClass):
    latitude = None
    longitude = None
    geoname_id = None

    geoname_data = None
    postalcode_data = None

    def __init__(self, **kwargs):
        super(Geoname, self).__init__(**kwargs)

        self.geoname_id = kwargs.get("geoname_id")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")

        if is_empty(self.latitude) and is_empty(self.longitude):
            self.latitude, self.longitude = getattr(settings, "LOCATION")

    def get_location(self):
        self.geoname_data = get_geoname_by_coords(self.latitude, self.longitude)
        self.postalcode_data = get_postal_code_by_coords(self.latitude, self.longitude)

        self.geoname_id = self.geoname_data.geonameid

    def get_local_time(self):
        return AwareDateTime(datetime.datetime.now(), self.time_zone)

    def get_weather(self):
        return Weather(self.latitude, self.longitude)

    @property
    def city(self):
        if is_empty(self.postalcode_data):
            self.get_location()
        return self.postalcode_data.city

    @property
    def state(self):
        if is_empty(self.postalcode_data):
            self.get_location()
        return self.postalcode_data.state

    @property
    def state_name(self):
        if is_empty(self.postalcode_data):
            self.get_location()
        return self.postalcode_data.admin_name1

    @property
    def zip_code(self):
        if is_empty(self.postalcode_data):
            self.get_location()
        return self.postalcode_data.postal_code

    @property
    def time_zone(self):
        if is_empty(self.geoname_data):
            self.get_location()
        return self.geoname_data.timezone

    @property
    def coordinates(self):
        return self.latitude, self.longitude
