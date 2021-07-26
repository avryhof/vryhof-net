import os
import zipfile

from api.utility_functions import import_geonames_csv
from utilities.command_baseclass import ManagementCommand

countries = ["AZ", "GU", "MP", "PR", "US", "VI"]


class Command(ManagementCommand):
    def handle(self, *args, **options):
        self._timer()

        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(app_dir, "data")
        dump_dir = os.path.join(data_dir, "dump")

        for country in countries:
            self._log_message("Import data for {}".format(country))
            zip_file = os.path.join(dump_dir, "{}.zip".format(country))
            txt_file = os.path.join(dump_dir, "{}.txt".format(country))

            zip_ref = zipfile.ZipFile(zip_file, "r")
            zip_ref.extractall(dump_dir)
            zip_ref.close()

            import_geonames_csv(txt_file)

        self._timer()
