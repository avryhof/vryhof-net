from api.models import GeoPostalCode
from gis.models import PostalCode
from utilities.command_baseclass import ManagementCommand


class Command(ManagementCommand):
    def handle(self, *args, **options):
        self._timer()

        for postal_code in PostalCode.objects.all():
            try:
                pc = GeoPostalCode.objects.get(postal_code=postal_code)
            except GeoPostalCode.DoesNotExist:
                pc = GeoPostalCode.objects.create(postal_code=postal_code)

            if pc.place is None:
                pc.link_place()

        self._timer()
