import datetime
import logging
import math
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from gis.constants import COUNTRIES
from gis.utility_functions import import_postal_codes_csv, get_geoname_data

logger = logging.getLogger(__name__)

settings.DEBUG = False

insert_threshold = 1000


class Command(BaseCommand):
    help = "Import Postal Codes from GeoNames."
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    init_time = None
    existing_drug_list = []
    drug_insert_list = []

    def _log_message(self, message):
        log_message = "%s: %s\n" % (datetime.datetime.now().isoformat()[0:19], message)

        logger.info(message)

        if self.verbosity > 0:
            self.stdout.write(log_message)

    def _timer(self):
        if not self.init_time:
            self.init_time = datetime.datetime.now()
            self._log_message("Command initiated.")
        else:
            self._log_message("Command completed.")

            complete_time = datetime.datetime.now()
            command_total_seconds = (complete_time - self.init_time).total_seconds()
            command_minutes = math.floor(command_total_seconds / 60)
            command_seconds = command_total_seconds - (command_minutes * 60)

            self._log_message("Command took %i minutes and %i seconds to run." % (command_minutes, command_seconds))

    def handle(self, *args, **options):
        self.verbosity = int(options["verbosity"])

        self._timer()

        data_path = get_geoname_data()

        for country in COUNTRIES:
            self._log_message("Processing: %s" % country)

            data_file_path = os.path.join(data_path, "zip", '{}.txt'.format(country))
            import_postal_codes_csv(data_file_path)

        self._timer()
