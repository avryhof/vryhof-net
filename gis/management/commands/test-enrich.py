from gis.enrich import Enrich
from utilities.command_baseclass import ManagementCommand


class Command(ManagementCommand):
    def handle(self, *args, **options):
        e = Enrich()
        pdl = e.by_name(name="Tasha", phone="3155099079")
