import pprint

import bleach
from gis.models import PostalCode
from gis.utility_functions import points_within_radius
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response


from assistant.api_auth import AnonymousAuthentication
from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AnonymousPermission



@api_view(["GET", "POST"])
@authentication_classes((AnonymousAuthentication,))
@permission_classes((AnonymousPermission,))
def get_zipcodes_in_radius(request, **kwargs):
    """
    Finds ZipCodes within a radius of the specified Zip Code
    :param request:
    :return:
    """

    zip_code = kwargs.get('zip_code', None)
    radius = kwargs.get('radius', False)
    distance_units = bleach.clean(kwargs.get('distance_units', 'miles'))

    if distance_units.lower() in ['mi', 'miles', 'imperial', 'empirical', 'us', 'united states', 'usa']:
        use_miles = True

    starting_zip_code = PostalCode.objects.get(postal_code=zip_code)

    zipcodes_in_radius = points_within_radius(
        PostalCode, starting_zip_code.latitude, starting_zip_code.longitude, radius=radius, use_miles=True)

    resp = {}

    zip_codes = []
    for zip_code in zipcodes_in_radius:
        zip_codes.append({
            "zip_code": zip_code.postal_code,
            "distance": round(zip_code.distance, 3),
            "city": zip_code.place_name,
            "state": zip_code.admin_code1
        })

    resp['zip_codes'] = zip_codes

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)
