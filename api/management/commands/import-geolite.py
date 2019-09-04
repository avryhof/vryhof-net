from __future__ import unicode_literals

import csv
import datetime
import glob
import logging
import math
import os
import pprint
import zipfile
from urllib.request import urlretrieve

from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import PostalCode, IP4Location, IP6Location
from api.utility_functions import import_postal_codes_csv
from utilities.aware_datetime import aware_datetime

logger = logging.getLogger(__name__)

datetime = aware_datetime()

settings.DEBUG = False

geolite_city = "https://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip"
# geolite_country = "https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country-CSV.zip"
# geolite_asn = "https://geolite.maxmind.com/download/geoip/database/GeoLite2-ASN-CSV.zip"


class Command(BaseCommand):
    help = "Import Postal Codes from GeoNames."
    verbosity = 0
    current_file = None
    log_file_name = None
    log_file = False

    init_time = None
    existing_drug_list = []
    drug_insert_list = []

    # def add_arguments(self, parser):
    #     parser.add_argument("address", type=str)

    def _log_message(self, message):
        log_message = "%s: %s\n" % (datetime.now().isoformat()[0:19], message)

        logger.info(message)

        if self.verbosity > 0:
            self.stdout.write(log_message)

    def _timer(self):
        if not self.init_time:
            self.init_time = datetime.now()
            self._log_message("Command initiated.")
        else:
            self._log_message("Command completed.")

            complete_time = datetime.now()
            command_total_seconds = (complete_time - self.init_time).total_seconds()
            command_minutes = math.floor(command_total_seconds / 60)
            command_seconds = command_total_seconds - (command_minutes * 60)

            self._log_message("Command took %i minutes and %i seconds to run." % (command_minutes, command_seconds))

    def handle(self, *args, **options):
        self.verbosity = int(options["verbosity"])

        self._timer()

        media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
        zip_file_path = os.path.join(media_root_normalized, 'maxmind')
        zip_file = os.path.join(zip_file_path, "GeoLite2-City-CSV.zip")

        if not os.path.exists(zip_file_path):
            os.makedirs(zip_file_path)

        if os.path.exists(zip_file):
            os.remove(zip_file)

        urlretrieve(geolite_city, zip_file)

        zip_ref = zipfile.ZipFile(zip_file, "r")
        zip_ref.extractall(zip_file_path)
        zip_ref.close()
        os.remove(zip_file)

        for folder in glob.glob(os.path.join(zip_file_path, "*")):
            if os.path.isdir(folder):
                for csv_file_name in glob.glob(os.path.join(folder, "GeoLite2-City-Blocks-*.csv")):
                    self._log_message("Processing %s" % csv_file_name)
                    if 'IPV4' in csv_file_name:
                        target_model = IP4Location
                    else:
                        target_model = IP6Location

                    data_file = open(csv_file_name, 'rU')

                    rows = csv.reader(data_file)
                    next(rows, None)

                    insert_list = []
                    for row in rows:
                        if len(row) > 0 and row[6]:
                            try:
                                ip = target_model.objects.get(
                                    network=row[0]
                                )

                            except target_model.DoesNotExist:
                                insert_list.append(target_model(
                                    network=row[0],
                                    geoname_id=row[1],
                                    registered_country_geoname_id=row[2],
                                    represented_country_geoname_id=row[3],
                                    is_anonymous_proxy=row[4] == "1",
                                    is_satellite_provider=row[5] == "1",
                                    postal_code=row[6],
                                    updated=datetime.now()
                                ))

                            else:
                                ip.network = row[0],
                                ip.geoname_id = row[1],
                                ip.registered_country_geoname_id = row[2],
                                ip.represented_country_geoname_id = row[3],
                                ip.is_anonymous_proxy = row[4],
                                ip.is_satellite_provider = row[5],
                                ip.postal_code = row[6],
                                ip.updated = datetime.now()
                                ip.save()

                            if len(insert_list) == 10000:
                                target_model.objects.bulk_create(insert_list)
                                print("Inserted 10,000 objects for a total of %i." % target_model.objects.count())
                                insert_list = []

                    data_file.close()

                    print("Inserted %i objects." % len(insert_list))
                    target_model.objects.bulk_create(insert_list)
                    print("%i objects total." % target_model.objects.count())
                    os.remove(csv_file_name)

                self._timer()
