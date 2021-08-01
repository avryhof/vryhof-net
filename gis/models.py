from math import radians, cos, sin, asin, sqrt

import requests
from django.db import models
from django.db.models import DO_NOTHING, DateTimeField

from gis.constants import ACCURACY_CHOICES, URBAN, SUBURBAN, RURAL, CLASS_URBAN, CLASS_SUBURBAN, CLASS_RURAL
from gis.us_census_class import USCensus
from gis.usps_class import USPS
from utilities.debugging import log_message


class GISPoint(models.Model):
    name = models.CharField(max_length=180, blank=True, null=True)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "%s,%s" % (str(self.latitude), str(self.longitude))

    def distance_from(self, latitude, longitude, **kwargs):
        use_miles = kwargs.get("use_miles", True)
        distance_unit = float(3959 if use_miles else 6371)

        latitude1 = radians(float(latitude))
        latitude2 = radians(float(self.latitude))

        longitude1 = radians(float(longitude))
        longitude2 = radians(float(self.longitude))

        distance_longitude = longitude2 - longitude1
        distance_latitude = latitude2 - latitude1

        a = sin(distance_latitude / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(distance_longitude / 2) ** 2
        c = 2 * asin(sqrt(a))

        distance = c * distance_unit

        return distance

    def in_radius(self, latitude, longitude, radius, **kwargs):
        return self.distance_from(latitude, longitude, **kwargs) < radius


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

    def density_classification(self):
        """
        By Census tract definitions:
        > 50000      = URBAN (U)
        >2500 <50000 = SUBURBAN (S)
        >10 <2500    = RURAL (R)
        <10          = FRONTIER (F)
        """
        if self.population >= URBAN:
            self.classification = "U"

        elif URBAN > self.population >= SUBURBAN:
            self.classification = "S"

        elif SUBURBAN >= self.population >= RURAL:
            self.classification = "R"

        else:
            self.classification = "F"

        self.save()


class PostalCode(GISPoint):
    place = models.ForeignKey(GeoName, null=True, on_delete=models.SET_NULL)
    country_code = models.CharField(max_length=2, blank=True, null=True)  # iso country code, 2 characters
    postal_code = models.CharField(max_length=20, blank=True, null=True)  # varchar(20)
    place_name = models.CharField(max_length=180, blank=True, null=True)  # varchar(180)
    admin_name1 = models.CharField(max_length=100, blank=True, null=True)  # 1. order subdivision (state) varchar(100)
    admin_code1 = models.CharField(max_length=20, blank=True, null=True)  # 1. order subdivision (state) varchar(20)
    admin_name2 = models.CharField(
        max_length=100, blank=True, null=True
    )  # 2. order subdivision (county/province) varchar(100)
    admin_code2 = models.CharField(
        max_length=20, blank=True, null=True
    )  # 2. order subdivision (county/province) varchar(20)
    admin_name3 = models.CharField(
        max_length=100, blank=True, null=True
    )  # 3. order subdivision (community) varchar(100)
    admin_code3 = models.CharField(max_length=20, blank=True, null=True)  # 3. order subdivision (community) varchar(20)
    accuracy = models.IntegerField(
        null=True, choices=ACCURACY_CHOICES
    )  # accuracy of lat/lng from 1=estimated, 4=geonameid, 6=centroid of addresses or shape
    updated = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.place_name

    @property
    def density(self):
        try:
            data = PopulationDensity.objects.get(postal_code=self)
        except PopulationDensity.DoesNotExist:
            return None
        else:
            return data

    @property
    def city(self):
        return self.place_name

    @property
    def state(self):
        return self.admin_code1

    def zip_code(self):
        return self.postal_code

    def as_dict(self):
        return dict(
            name=self.name,
            latitude=self.latitude,
            longitude=self.longitude,
            country_code=self.country_code,
            postal_code=self.postal_code,
            place_name=self.place_name,
            admin_name1=self.admin_name1,
            admin_code1=self.admin_code1,
            admin_name2=self.admin_name2,
            admin_code2=self.admin_code2,
            admin_name3=self.admin_name3,
            admin_code3=self.admin_code3,
            accuracy=self.accuracy,
            updated=self.updated,
        )

    def link_place_api(self):
        resp = requests.get("https://firefox.vryhof.net/api/rest/zipcode/{}/".format(self.postal_code))
        resp_json = resp.json()
        if "place" in resp_json:
            place_id = resp_json.get("place").get("geonameid")
            place = GeoName.objects.get(geonameid=place_id)
            try:
                self.place = place
            except GeoName.DoesNotExist:
                log_message("Place not found")
            else:
                self.save()

    def link_place(self):
        place = False
        try:
            place = GeoName.objects.get(
                name__iexact=self.name,
                country_code=self.country_code,
                admin1_code=self.admin_code1,
                admin2_code=self.admin_code2,
                feature_class="P",
            )
        except GeoName.DoesNotExist:
            try:
                place = GeoName.objects.get(
                    name__iexact=self.name,
                    country_code=self.country_code,
                    admin1_code=self.admin_code1,
                    feature_class="P",
                )
            except GeoName.DoesNotExist:
                try:
                    place = GeoName.objects.get(
                        name__iexact=self.name, country_code=self.country_code, admin1_code=self.admin_code1,
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


class PopulationDensity(models.Model):
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    population = models.IntegerField(null=True)
    land_miles = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    density = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    classification = models.CharField(max_length=12, blank=True, null=True)
    postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)

    def as_dict(self):
        self.set_classification()
        return dict(
            population=self.population,
            land_miles=self.land_miles,
            population_density=self.density,
            classification=self.classification,
        )

    def set_classification(self):
        if self.density > 3000:
            self.classification = CLASS_URBAN
        elif 1000 < self.density < 3000:
            self.classification = CLASS_SUBURBAN
        elif self.density < 1000:
            self.classification = CLASS_RURAL

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


class AbstractStreetAddress(GISPoint):
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=180, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    plus_four = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.ForeignKey(PostalCode, blank=True, null=True, on_delete=DO_NOTHING)
    validated = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def dict(self):
        return dict(
            address1=self.address1, address2=self.address2, city=self.city, state=self.state, zip_code=self.zip_code
        )

    def geocode(self, **kwargs):
        debug = kwargs.get("debug", False)

        retn = False

        if self.latitude and self.longitude:
            retn = True

        else:
            valid_address = self.normalize()

            # log_message(valid_address, pretty=True, custom_log="pharmacy.log")
            if debug:
                print(valid_address)

            try:
                verified_address = VerifiedStreetAddress.objects.get(
                    address1__iexact=self.address1,
                    address2__iexact=self.address2,
                    city__iexact=self.city,
                    state__iexact=self.state,
                    zip_code=self.zip_code,
                    postal_code=self.postal_code,
                )

            except VerifiedStreetAddress.DoesNotExist:
                usc = USCensus()

                if valid_address:
                    if valid_address.get("address1") and valid_address.get("city") and valid_address.get("state"):
                        geocoded = usc.geocode(query=valid_address)
                        if geocoded:
                            retn = True
                            self.latitude = geocoded.get("latitude")
                            self.longitude = geocoded.get("longitude")
                            self.save()

            else:
                self.address1 = verified_address.address1
                self.address2 = verified_address.address2
                self.city = verified_address.city
                self.state = verified_address.state
                self.zip_code = verified_address.zip_code
                self.plus_four = verified_address.plus_four
                self.postal_code = verified_address.postal_code
                self.validated = verified_address.validated
                self.save()

        if debug:
            # log_message(retn, pretty=True, custom_log="pharmacy.log")
            print(retn)

        return retn

    def link_postal_code(self, zip_code=False):
        retn = False

        if not self.postal_code:
            if not zip_code:
                zip_code = self.zip_code

            try:
                self.postal_code = PostalCode.objects.get(postal_code=zip_code)

            except PostalCode.DoesNotExist:
                log_message("Postal code not found: {}".format(zip_code))

            else:
                retn = True
                if not self.state:
                    self.state = self.postal_code.state
                self.save()
        else:
            retn = True

        return retn

    def normalize(self):
        valid_address = dict(
            address1=self.address1,
            address2=self.address2,
            city=self.city,
            state=self.state,
            zip_code=self.zip_code,
            plus_four=self.plus_four,
        )

        if not self.validated:
            search_address = self.dict()
            ps = USPS()
            valid_address = ps.address(**search_address)

            if valid_address:
                self.address1 = valid_address.get("address1", self.address1)
                self.address2 = valid_address.get("address2", self.address2)
                self.city = valid_address.get("city", self.city)
                self.state = valid_address.get("state", self.state)
                self.zip_code = valid_address.get("zip_code", self.zip_code)
                self.plus_four = valid_address.get("plus_four", self.plus_four)
                self.validated = True
                self.save()

        return valid_address


class VerifiedStreetAddress(AbstractStreetAddress):
    updated = DateTimeField(auto_now_add=True)


class ZCTACrossWalk(models.Model):
    zip_code = models.CharField(max_length=9, blank=True, null=True)
    po_name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    zip_type = models.CharField(max_length=255, blank=True, null=True)
    zcta = models.CharField(max_length=9, blank=True, null=True)
    zip_join_type = models.CharField(max_length=128, blank=True, null=True)
    postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)

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

        if self.state is None and self.postal_code is not None:
            self.state = self.postal_code.state
            self.save()


class BasePopulation(models.Model):
    geoid = models.CharField(max_length=128, primary_key=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    universe = models.DecimalField(max_digits=9, decimal_places=1, null=True)
    universe_annotation = models.DecimalField(max_digits=9, decimal_places=1, null=True)
    universe_moe = models.CharField(max_length=128, blank=True, null=True)
    universe_moe_annotation = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        abstract = True


class ZCTAState(models.Model):
    state = models.CharField(max_length=6, blank=True, null=True)
    admin_name1 = models.CharField(max_length=100, blank=True, null=True)
    admin_code1 = models.CharField(max_length=20, blank=True, null=True)

    def link_names(self):
        if self.admin_code1 is None or self.admin_name1 is None:
            zctas = ZCTAZcta.objects.filter(state=self.state)
            zcta = zctas[0]

            try:
                crosswalk = ZCTACrossWalk.objects.get(zcta=zcta.zcta)
            except ZCTACrossWalk.DoesNotExist:
                pass
            else:
                self.admin_code1 = crosswalk.state

                if crosswalk.postal_code is not None:
                    self.admin_name1 = crosswalk.postal_code.admin_name1

                self.save()


class ZCTAPlace(BasePopulation):
    state = models.CharField(max_length=6, blank=True, null=True)
    place = models.CharField(max_length=128, blank=True, null=True)
    geonames_place = models.ForeignKey(GeoName, null=True, on_delete=models.SET_NULL)


class ZCTAZcta(BasePopulation):
    state = models.CharField(max_length=6, blank=True, null=True)
    zcta = models.CharField(max_length=9, blank=True, null=True)
    geonames_postal_code = models.ForeignKey(PostalCode, null=True, on_delete=models.SET_NULL)

    def link_postal_code(self):
        if self.geonames_postal_code is None:
            try:
                zcta_cross = ZCTACrossWalk.objects.get(zcta=self.zcta)
            except ZCTACrossWalk.DoesNotExist:
                pass
            else:
                self.geonames_postal_code = zcta_cross.postal_code
                self.save()
