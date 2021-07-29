import os
import pprint

from census_data_downloader.tables import PopulationDownloader
from django.conf import settings

from gis.models import ZCTAPlace, ZCTAZcta, ZCTAState
from gis.utility_functions import file_is_expired
from utilities.command_baseclass import ManagementCommand
from utilities.debugging import log_message
from utilities.excel import csv_to_dicts
from utilities.utility_functions import decimal_or_null


class Command(ManagementCommand):
    def normalize_keys(self, input_dict):
        output_dict = dict()
        for key, val in input_dict.items():
            key = key.replace("metropolitan statistical area/micropolitan statistical area", "msa")
            output_dict[key.strip().lower().replace(" ", "_")] = val
        return output_dict

    def load_data(self, csv_file, db_model):
        db_model.objects.all().delete()
        for item in csv_to_dicts(csv_file):
            db_model.objects.create(**self.normalize_keys(item))

    def handle(self, *args, **options):
        self._timer()

        media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
        data_dir = os.path.join(media_root_normalized, "zcta-data")

        csv_places = os.path.join(data_dir, "processed", "acs5_2019_population_places.csv")
        csv_zctas = os.path.join(data_dir, "processed", "acs5_2019_population_zctas.csv")

        if file_is_expired(csv_places) or file_is_expired(csv_zctas):
            log_message("Downloading files")
            downloader = PopulationDownloader(settings.CENSUS_API_KEY, data_dir=data_dir)
            downloader.download_zctas()
            downloader.download_places()

        log_message("Loading Places")
        places = csv_to_dicts(csv_places)
        insert_list = []
        for place in places:
            try:
                ZCTAPlace.objects.get(geoid=place.get("geoid"))
            except ZCTAPlace.DoesNotExist:
                insert_list.append(ZCTAPlace(
                    geoid=place.get("geoid"),
                    name=place.get("name"),
                    universe=decimal_or_null(place.get("universe")),
                    universe_annotation=decimal_or_null(place.get("universe_annotation")),
                    universe_moe=place.get("universe_moe"),
                    universe_moe_annotation=place.get("universe_moe_annotation"),
                    state=place.get("state"),
                    place=place.get("place")
                ))

            if len(insert_list) == 10000:
                ZCTAPlace.objects.bulk_create(insert_list)
                insert_list = []

        ZCTAPlace.objects.bulk_create(insert_list)
        insert_list = []

        log_message("Loading ZCTAs")
        zctas = csv_to_dicts(csv_zctas)
        for zcta in zctas:
            try:
                zcta_zcta = ZCTAZcta.objects.get(geoid=zcta.get("geoid"))
            except ZCTAZcta.DoesNotExist:
                insert_list.append(ZCTAZcta(
                    geoid=zcta.get("geoid"),
                    name=zcta.get("name"),
                    universe=decimal_or_null(zcta.get("universe")),
                    universe_annotation=decimal_or_null(zcta.get("universe_annotation")),
                    universe_moe=zcta.get("universe_moe"),
                    universe_moe_annotation=zcta.get("universe_moe_annotation"),
                    state=zcta.get("state"),
                    zcta=zcta.get("zip code tabulation area")
                ))

            if len(insert_list) == 10000:
                ZCTAZcta.objects.bulk_create(insert_list)
                insert_list = []

        ZCTAZcta.objects.bulk_create(insert_list)
        insert_list = []

        log_message("Linking Postal codes.")
        for zcta in ZCTAZcta.objects.filter(geonames_postal_code__isnull=True):
            zcta.link_postal_code()

        log_message("Building State crosswalk")
        state_codes = list(set(ZCTAZcta.objects.all().values_list("state", flat=True)))
        for state_code in state_codes:
            try:
                state = ZCTAState.objects.get(state=state_code)
            except ZCTAState.DoesNotExist:
                state = ZCTAState.objects.create(state=state_code)

            state.link_names()

        self._timer()
