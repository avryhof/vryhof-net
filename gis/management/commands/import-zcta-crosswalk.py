import os

from django.conf import settings

from gis.models import ZCTACrossWalk
from gis.utility_functions import file_is_expired, download_new_file
from utilities.command_baseclass import ManagementCommand
from utilities.debugging import log_message
from utilities.excel import excel_to_dicts, csv_to_dicts


class Command(ManagementCommand):
    def handle(self, *args, **options):
        self._timer()

        media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
        data_dir = os.path.join(media_root_normalized, "zcta-data")

        if not os.path.exists(data_dir):
            log_message("Creating directory: {}".format(data_dir))
            os.makedirs(data_dir)

        xls_crosswalk_link = "https://udsmapper.org/wp-content/uploads/2020/09/Zip_to_zcta_crosswalk_2020.xlsx"
        csv_crosswalk_link = "https://raw.githubusercontent.com/censusreporter/acs-aggregate/master/crosswalks/zip_to_zcta/zip_zcta_xref.csv"

        xls_crosswalk_file = os.path.join(data_dir, "crosswalk.xlsx")
        csv_crosswalk_file = os.path.join(data_dir, "crosswalk.csv")

        if file_is_expired(xls_crosswalk_file, 30):
            download_new_file(xls_crosswalk_link, xls_crosswalk_file)

        if file_is_expired(csv_crosswalk_file, 30):
            download_new_file(csv_crosswalk_link, csv_crosswalk_file)

        log_message("Loading: {}".format(xls_crosswalk_file))
        xls_zctas = excel_to_dicts(xls_crosswalk_file)
        log_message("Importing {} data points.".format(len(xls_zctas)))
        for xls_zcta in xls_zctas:
            zip_code = xls_zcta.get("ZIP_CODE")
            po_name = xls_zcta.get("PO_NAME")
            state = xls_zcta.get("STATE")
            zip_type = xls_zcta.get("ZIP_TYPE")
            zcta_value = xls_zcta.get("ZCTA")
            zip_join_type = xls_zcta.get("zip_join_type")
            try:
                zcta = ZCTACrossWalk.objects.get(zcta=zcta_value)
            except ZCTACrossWalk.DoesNotExist:
                zcta = ZCTACrossWalk.objects.create(
                    zcta=zcta_value,
                    zip_code=zip_code,
                    po_name=po_name,
                    state=state,
                    zip_type=zip_type,
                    zip_join_type=zip_join_type
                )

            zcta.link_postal_code()

        log_message("Loading: {}".format(csv_crosswalk_file))
        csv_zctas = csv_to_dicts(csv_crosswalk_file)
        log_message("Importing {} data points.".format(len(csv_zctas)))
        for csv_zcta in csv_zctas:
            zip_code = csv_zcta.get("zip_code")
            zcta_value = csv_zcta.get("zcta")
            zip_type = csv_zcta.get("source")

            try:
                zcta = ZCTACrossWalk.objects.get(zcta=zcta_value)
            except ZCTACrossWalk.DoesNotExist:
                zcta = ZCTACrossWalk.objects.create(
                    zcta=zcta_value,
                    zip_code=zip_code,
                    zip_type=zip_type,
                )

            zcta.link_postal_code()

        self._timer()

