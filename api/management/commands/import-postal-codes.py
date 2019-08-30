from __future__ import unicode_literals

import csv
import datetime
import logging
import math
import os
import zipfile
from urllib.request import urlretrieve

from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import PostalCode
from utilities.aware_datetime import aware_datetime

logger = logging.getLogger(__name__)

datetime = aware_datetime()

settings.DEBUG = False


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
        zip_file_path = os.path.join(media_root_normalized, 'geonames')
        zip_file = os.path.join(zip_file_path, 'US.zip')

        if not os.path.exists(zip_file_path):
            os.makedirs(zip_file_path)

        if os.path.exists(zip_file):
            os.remove(zip_file)

        urlretrieve("http://download.geonames.org/export/zip/US.zip", zip_file)

        zip_ref = zipfile.ZipFile(zip_file, "r")
        zip_ref.extractall(zip_file_path)
        zip_ref.close()
        os.remove(zip_file)

        data_file_path = os.path.join(zip_file_path, 'US.txt')

        data_file = open(data_file_path, 'rU')

        rows = csv.reader(data_file, delimiter='\t')

        insert_list = []
        for row in rows:
            if len(row) > 0 and row[11]:
                try:
                    postal_code = PostalCode.objects.get(
                        postal_code=row[1],
                        name=row[2],
                        place_name=row[2]
                    )

                except PostalCode.DoesNotExist:
                    insert_list.append(PostalCode(
                        country_code=row[0],
                        postal_code=row[1],
                        name=row[2],
                        place_name=row[2],
                        admin_name1=row[3],
                        admin_code1=row[4],
                        admin_name2=row[5],
                        admin_code2=row[6],
                        admin_name3=row[7],
                        admin_code3=row[8],
                        latitude=row[9],
                        longitude=row[10],
                        accuracy=row[11],
                        updated=datetime.now()
                    ))

                else:
                    postal_code.country_code = row[0]
                    postal_code.postal_code = row[1]
                    postal_code.name = row[2]
                    postal_code.place_name = row[2]
                    postal_code.admin_name1 = row[3]
                    postal_code.admin_code1 = row[4]
                    postal_code.admin_name2 = row[5]
                    postal_code.admin_code2 = row[6]
                    postal_code.admin_name3 = row[7]
                    postal_code.admin_code3 = row[8]
                    postal_code.latitude = row[9]
                    postal_code.longitude = row[10]
                    postal_code.accuracy = row[11]
                    postal_code.updated = datetime.now()
                    postal_code.save()

        data_file.close()

        PostalCode.objects.bulk_create(insert_list)

        os.remove(data_file_path)

        self._timer()
