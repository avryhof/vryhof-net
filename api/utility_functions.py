from api.models import PostalCode
from gis.utility_functions import points_within_radius


def postal_codes_within_radius(latitude, longitude, **kwargs):

    return points_within_radius(PostalCode, latitude, longitude, **kwargs)
