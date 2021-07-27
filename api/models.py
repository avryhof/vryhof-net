from json import JSONDecodeError

import requests
from django.db import models

from gis.models import GISPoint, PostalCode
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


class GeoName(GISPoint):
    geonameid = models.IntegerField(primary_key=True)
    asciiname = models.CharField(max_length=200, blank=True, null=True)
    alternatenames = models.TextField(null=True)
    feature_class = models.CharField(max_length=1, blank=True, null=True)
    feature_code = models.CharField(max_length=10, blank=True, null=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    cc2 = models.CharField(max_length=200, blank=True, null=True)
    admin1_code = models.CharField(max_length=20, blank=True, null=True)  # 1. order subdivision (state) varchar(20)
    admin2_code = models.CharField(max_length=80, blank=True, null=True)  # 2. order subdivision (county/province)
    admin3_code = models.CharField(max_length=20, blank=True, null=True)  # 3. order subdivision (community) varchar(20)
    admin4_code = models.CharField(max_length=20, blank=True, null=True)  # 3. order subdivision (community) varchar(20)
    population = models.BigIntegerField(null=True)
    elevation = models.IntegerField(null=True)  # in meters
    dem = models.IntegerField(null=True)  # digital elevation model, srtm3 or gtopo30
    timezone = models.CharField(max_length=40, blank=True, null=True)
    modification_date = models.DateField(null=True)
    postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)

    def as_dict(self):
        retn = dict(
            geonameid=self.geonameid,
            asciiname=self.asciiname,
            alternatenames=self.alternatenames,
            feature_class=self.feature_class,
            feature_code=self.feature_code,
            country_code=self.country_code,
            cc2=self.cc2,
            admin1_code=self.admin1_code,  # 1. order subdivision (state) varchar(20)
            admin2_code=self.admin2_code,  # 2. order subdivision (county/province)
            admin3_code=self.admin3_code,  # 3. order subdivision (community) varchar(20)
            admin4_code=self.admin4_code,  # 3. order subdivision (community) varchar(20)
            population=self.population,
            elevation=self.elevation,  # in meters
            dem=self.dem,  # digital elevation model, srtm3 or gtopo30
            timezone=self.timezone,
            modification_date=self.modification_date,
        )
        if self.postal_code is not None:
            retn.update(postal_code=self.postal_code.as_dict())
            try:
                pd = PopulationDensity.objects.get(postal_code=self.postal_code)
            except PopulationDensity.DoesNotExist:
                pass
            else:
                retn.update(population=pd.as_dict())
        return retn


class GeoPostalCode(models.Model):
    postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)
    place = models.ForeignKey(GeoName, null=True, on_delete=models.SET_NULL)

    def as_dict(self):
        retn = {}

        pd = False
        if self.postal_code is not None:
            retn.update(postal_code=self.postal_code.as_dict())

            try:
                pd = PopulationDensity.objects.get(postal_code=self.postal_code)
            except PopulationDensity.DoesNotExist:
                pass

        if self.place is not None:
            retn.update(place=self.place.as_dict())
            if not pd:
                try:
                    pd = PopulationDensity.objects.get(place=self.place)
                except PopulationDensity.DoesNotExist:
                    pass

        if pd:
            retn.update(density=pd.as_dict())

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


class PopulationDensity(models.Model):
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    population = models.IntegerField(null=True)
    land_miles = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    density = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    classification = models.CharField(max_length=1, blank=True, null=True)
    postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)
    place = models.ForeignKey(GeoName, null=True, on_delete=models.SET_NULL)

    def as_dict(self):
        return dict(
            population=self.population,
            land_miles=self.land_miles,
            density=self.density,
            classification=self.classification,
        )

    def set_classification(self):
        if self.density > 3000:
            self.classification = "U"
        elif 1000 < self.density < 3000:
            self.classification = "S"
        elif 6 < self.density < 1000:
            self.classification = "R"
        elif self.density < 6:
            self.classification = "F"

        self.save()

    def link_postal_code(self):
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
        if self.use_api_search:
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
