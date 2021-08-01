from dateutil.parser import parse
from django.core.management import BaseCommand

from catalog.models import Location, LocationCapability
from catalog.square_base import square_client
from catalog.utils import geocode


class Command(BaseCommand):
    def handle(self, *args, **options):
        api_locations = square_client.locations

        # Call list_locations method to get all locations in this Square account
        result = api_locations.list_locations()
        # Call the success method to see if the call succeeded
        if result.is_success():
            # The body property is a list of locations
            locations = result.body["locations"]

            for location in locations:
                try:
                    loc = Location.objects.get(location_id=location.get("id"))
                except Location.DoesNotExist:
                    loc = Location.objects.create(
                        location_id=location.get("id"),
                        name=location.get("name"),
                        business_name=location.get("business_name"),
                        country=location.get("country"),
                        created_at=parse(location.get("created_at")),
                        currency=location.get("currency"),
                        language_code=location.get("language_code"),
                        mcc=location.get("mcc"),
                        merchant_id=location.get("merchant_id"),
                        location_status=location.get("status"),
                        location_type=location.get("type"),
                        address1=location.get("address").get("address_line_1"),
                        address2=location.get("address").get("address_line_2"),
                        city=location.get("address").get("locality"),
                        zip_code=location.get("address").get("postal_code"),
                    )
                    capabilities = location.get("capabilities")
                    for capability in capabilities:
                        try:
                            LocationCapability.objects.get(location=loc, capability=capability)
                        except LocationCapability.DoesNotExist:
                            LocationCapability.objects.create(location=loc, capability=capability)
                    LocationCapability.objects.filter(location=loc).exclude(capability__in=capabilities).delete()

                    loc.link_postal_code(loc.zip_code)
                    loc.normalize()
                    loc.geocode()
                else:
                    if not loc.postal_code:
                        loc.link_postal_code()
                    if not loc.latitude or not loc.longitude:
                        geocode(loc)

        # Call the error method to see if the call failed
        elif result.is_error():
            print("Error calling LocationsApi.listlocations")
            errors = result.errors
            # An error is returned as a list of errors
            for error in errors:
                # Each error is represented as a dictionary
                for key, value in error.items():
                    print(f"{key} : {value}")
                print("\n")
