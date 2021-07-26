import os

from api.models import PopulationDensity
from gis.models import PostalCode
from utilities.command_baseclass import ManagementCommand
from utilities.excel import csv_to_dicts


class Command(ManagementCommand):
    def handle(self, *args, **options):
        self._timer()

        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        data_dir = os.path.join(app_dir, "data")
        density_file = os.path.join(data_dir, "Zipcode-ZCTA-Population-Density-And-Area-Unsorted.csv")

        zips = csv_to_dicts(density_file)
        for zipcode in zips:
            zip_code = zipcode.get("Zip/ZCTA")
            population = zipcode.get("2010 Population")
            land_area = zipcode.get("Land-Sq-Mi")
            density = zipcode.get("Density Per Sq Mile")
            try:
                zc = PopulationDensity.objects.get(zip_code=zip_code)
            except PopulationDensity.DoesNotExist:
                try:
                    postal_code = PostalCode.objects.get(postal_code=zip_code)
                except PostalCode.DoesNotExist:
                    postal_code = None

                PopulationDensity.objects.create(
                    zip_code=zip_code,
                    population=population,
                    land_miles=land_area,
                    density=density,
                    postal_code=postal_code,
                )
            else:
                zc.population = population
                zc.land_miles = land_area
                zc.density = density

                zc.save()

        for x in PopulationDensity.objects.all():
            if x.postal_code is None:
                x.link_postal_code()
            if x.place is None:
                x.link_place()

        self._timer()
