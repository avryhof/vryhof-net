import os

from django.conf import settings

from gis.models import PopulationDensity
from gis.utility_functions import file_is_expired, download_new_file
from utilities.command_baseclass import ManagementCommand
from utilities.debugging import log_message
from utilities.excel import csv_to_dicts


class Command(ManagementCommand):
    def handle(self, *args, **options):
        self._timer()

        media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
        data_dir = os.path.join(media_root_normalized, "density-data")

        if not os.path.exists(data_dir):
            log_message("Creating directory: {}".format(data_dir))
            os.makedirs(data_dir)

        density_file = os.path.join(data_dir, "ZCTA-DENSITY.csv")
        if file_is_expired(density_file, 30):
            download_new_file(
                "https://s3.amazonaws.com/SplitwiseBlogJB/Zipcode-ZCTA-Population-Density-And-Area-Unsorted.csv",
                density_file,
            )

        zips = csv_to_dicts(density_file)
        for zipcode in zips:
            zip_code = zipcode.get("Zip/ZCTA")
            population = int(zipcode.get("2010 Population"))
            land_area = float(zipcode.get("Land-Sq-Mi"))
            density = float(zipcode.get("Density Per Sq Mile"))

            try:
                zc = PopulationDensity.objects.get(zip_code=zip_code)
            except PopulationDensity.DoesNotExist:
                zc = PopulationDensity.objects.create(
                    zip_code=zip_code, population=population, land_miles=land_area, density=density
                )

            else:
                zc.population = population
                zc.land_miles = land_area
                zc.density = density

                zc.save()

            zc.set_classification()
            zc.link_postal_code()

        self._timer()
