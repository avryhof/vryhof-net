import os
import zipfile

from api.utility_functions import import_geonames_csv
from gis.constants import COUNTRIES
from gis.utility_functions import get_geoname_data
from utilities.command_baseclass import ManagementCommand

countries = ["AZ", "GU", "MP", "PR", "US", "VI"]


class Command(ManagementCommand):
    def handle(self, *args, **options):
        self._timer()

        data_path = get_geoname_data()
        dump_dir = os.path.join(data_path, "dump")

        self._log_message("Processing files in {}".format(dump_dir))

        for country in COUNTRIES:
            self._log_message("Import data for {}".format(country))
            zip_file = os.path.join(dump_dir, "{}.zip".format(country))
            txt_file = os.path.join(dump_dir, "{}.txt".format(country))

            try:
                zip_ref = zipfile.ZipFile(zip_file, "r")
            except zipfile.BadZipFile:
                self._log_message("Bad Zip File: {}".format(zip_file))
            else:
                zip_ref.extractall(dump_dir)
                zip_ref.close()

                import_geonames_csv(txt_file)

        self._timer()
