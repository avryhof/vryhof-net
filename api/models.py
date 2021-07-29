from json import JSONDecodeError

import requests
from django.db import models

from gis.models import GISPoint, PostalCode, GeoName, PopulationDensity
from utilities.debugging import log_message
from utilities.utility_functions import make_list


class IP4Location(GISPoint):
    network = models.CharField(max_length=128)
    geoname_id = models.CharField(max_length=180, blank=True, null=True)
    registered_country_geoname_id = models.CharField(max_length=180, blank=True, null=True)
    represented_country_geoname_id = models.CharField(max_length=180, blank=True, null=True)
    is_anonymous_proxy = models.BooleanField(default=False)
    is_satellite_provider = models.BooleanField(default=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # varchar(20)
    updated = models.DateTimeField(auto_now_add=True, null=True)


class IP6Location(GISPoint):
    network = models.CharField(max_length=255)
    geoname_id = models.CharField(max_length=180, blank=True, null=True)
    registered_country_geoname_id = models.CharField(max_length=180, blank=True, null=True)
    represented_country_geoname_id = models.CharField(max_length=180, blank=True, null=True)
    is_anonymous_proxy = models.BooleanField(default=False)
    is_satellite_provider = models.BooleanField(default=False)
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # varchar(20)
    updated = models.DateTimeField(auto_now_add=True, null=True)


class GeoPostalCode(models.Model):
    postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)
    place = models.ForeignKey(GeoName, null=True, on_delete=models.SET_NULL)

    def as_dict(self):
        retn = {}

        latitude = False
        longitude = False

        pd = False
        if self.postal_code is not None:
            retn = self.postal_code.as_dict()

            latitude = self.postal_code.latitude
            longitude = self.postal_code.longitude

            try:
                pd = PopulationDensity.objects.get(postal_code=self.postal_code)
            except PopulationDensity.DoesNotExist:
                pass

        if self.place is not None:
            retn.update(place=self.place.as_dict())

            if not latitude or not longitude:
                latitude = self.place.latitude
                longitude = self.place.longitude

            if not pd:
                try:
                    pd = PopulationDensity.objects.get(place=self.place)
                except PopulationDensity.DoesNotExist:
                    pass

        if pd:
            retn.update(pd.as_dict())

        # if latitude and longitude:
        #     w = Wikipedia()
        #     retn.update(wikipedia=w.get_by_coordinates(latitude, longitude))

        return retn

    def link_postal_code(self):
        if self.postal_code is None:
            try:
                self.postal_code = PostalCode.objects.get(postal_code=self.zip_code)
            except PostalCode.DoesNotExist:
                pass
            except PostalCode.MultipleObjectsReturned:
                if self.zip_code is not None:
                    postal_codes = PostalCode.objects.filter(postal_code=self.zip_code).order_by("accuracy")
                    if len(postal_codes) > 0:
                        self.postal_code = postal_codes[0]
                        self.save()
            else:
                self.save()

    def link_place_api(self):
        resp = requests.get(
            "http://api.geonames.org/findNearbyPlaceNameJSON",
            params=dict(lat=self.postal_code.latitude, lng=self.postal_code.longitude, username="avryhof"),
        )
        try:
            resp_json = resp.json()
        except JSONDecodeError:
            log_message("Turning off api search.")
            self.use_api_search = False
        else:
            if "geonames" in resp_json:
                places_json = make_list(resp_json.get("geonames"))
                place_json = places_json[0]
                place_id = place_json.get("geonameId")

                try:
                    self.place = GeoName.objects.get(geonameid=place_id)
                except GeoName.DoesNotExist:
                    log_message("Place not found")
                else:
                    self.postal_code.place_name = place_json.get("name")
                    self.postal_code.save()

                    self.save()

    def link_place(self):
        if not self.postal_code:
            self.link_postal_code()

        if self.postal_code:
            place = False
            try:
                place = GeoName.objects.get(
                    name__iexact=self.postal_code.name,
                    country_code=self.postal_code.country_code,
                    admin1_code=self.postal_code.admin_code1,
                    admin2_code=self.postal_code.admin_code2,
                    feature_class="P",
                )
            except GeoName.DoesNotExist:
                try:
                    place = GeoName.objects.get(
                        name__iexact=self.postal_code.name,
                        country_code=self.postal_code.country_code,
                        admin1_code=self.postal_code.admin_code1,
                        feature_class="P",
                    )
                except GeoName.DoesNotExist:
                    try:
                        place = GeoName.objects.get(
                            name__iexact=self.postal_code.name,
                            country_code=self.postal_code.country_code,
                            admin1_code=self.postal_code.admin_code1,
                        )
                    except (GeoName.DoesNotExist, GeoName.MultipleObjectsReturned):
                        self.link_place_api()

                except GeoName.MultipleObjectsReturned:
                    self.link_place_api()

            except GeoName.MultipleObjectsReturned:
                self.link_place_api()

            if place:
                self.place = place
                self.save()

        if not self.place.postal_code and self.postal_code:
            self.place.postal_code = self.postal_code
            self.place.save()
