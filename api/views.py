import bleach
import openai
from django.conf import settings
from duckduckgo_search import ddg
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import GeoPostalCode
from gis.models import PostalCode
from gis.utility_functions import points_within_radius
from livechat.helpers import get_chat_session
from utilities.helpers import get_client_ip
from utilities.utility_functions import is_empty

openai.api_key = getattr(settings, "OPENAI_API_KEY")


@api_view(["GET", "POST"])
def get_zipcodes_in_radius(request, **kwargs):
    """
    Finds ZipCodes within a radius of the specified Zip Code
    :param request:
    :return:
    """

    zip_code = kwargs.get("zip_code", None)
    radius = kwargs.get("radius", False)
    distance_units = bleach.clean(kwargs.get("distance_units", "miles"))

    if distance_units.lower() in ["mi", "miles", "imperial", "empirical", "us", "united states", "usa"]:
        use_miles = True

    starting_zip_code = PostalCode.objects.get(postal_code=zip_code)

    zipcodes_in_radius = points_within_radius(
        PostalCode, starting_zip_code.latitude, starting_zip_code.longitude, radius=radius, use_miles=True
    )

    resp = {}

    zip_codes = []
    for zip_code in zipcodes_in_radius:
        zip_codes.append(
            {
                "zip_code": zip_code.postal_code,
                "distance": round(zip_code.distance, 3),
                "city": zip_code.place_name,
                "state": zip_code.admin_code1,
            }
        )

    resp["zip_codes"] = zip_codes

    return Response(resp, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def zipcode_to_geoname(request, **kwargs):
    """
    Finds ZipCodes within a radius of the specified Zip Code
    :param request:
    :return:
    """

    zip_code = kwargs.get("zip_code", None)

    try:
        gpc = GeoPostalCode.objects.get(postal_code__postal_code=zip_code)
    except GeoPostalCode.DoesNotExist:
        resp = {"error": "Zip code not found."}
    else:
        gpc.link_postal_code()
        if gpc.place is not None:
            resp = gpc.as_dict()
        else:
            resp = {"error": "Place not found"}

    return Response(resp, status=status.HTTP_200_OK)


@api_view(["POST"])
def search(request, **kwargs):
    ddg_region = "us-en"

    keywords = request.data.get("q")

    resp = dict(chat=None, results=[], answers=[])

    chat_session = get_chat_session(request)
    try:
        bot = chat_session.bot(client_ip=get_client_ip(request), debug=False)

    except Exception as e:
        pass

    else:
        resp["chat"], response_source = bot.respond(keywords)

    ddg_keywords = keywords
    if not is_empty(chat_session.latitude) and not is_empty(chat_session.longitude):
        location = chat_session.geo
        loc = f"{location.city}, {location.state}"
        ddg_keywords = f"{keywords} location:{loc}"

    resp["results"] = ddg(ddg_keywords, region=ddg_region, safesearch="Off", time="y")
    # resp["answers"] = ddg_answers(ddg_keywords, related=False, output=None)

    # log_message(resp, pretty=True)

    return Response(resp, status=status.HTTP_200_OK)
