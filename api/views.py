import bleach
import openai
from django.conf import settings
from duckduckgo_search import ddg, ddg_answers, ddg_images
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response

from api.models import GeoPostalCode
from api.rest_auth import CsrfExemptSessionAuthentication
from gis.models import PostalCode
from gis.utility_functions import points_within_radius

openai.api_key = getattr(settings, "OPENAI_API_KEY")


@api_view(["GET", "POST"])
@authentication_classes((CsrfExemptSessionAuthentication))
@permission_classes(())
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
@authentication_classes(())
@permission_classes(())
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
@authentication_classes(())
@permission_classes(())
def search(request, **kwargs):
    ddg_region = "us-en"

    keywords = request.data.get("q")

    resp = dict(chat=None, results=[])

    try:
        completions = openai.Completion.create(
            engine="text-davinci-002",
            prompt=keywords,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

    except Exception as e:
        pass

    else:
        resp["chat"] = completions.choices[0].text.strip()

    resp["results"] = ddg(keywords, region=ddg_region, safesearch="Off", time="y")
    # resp["images"] = ddg_images(
    #     keywords,
    #     region=ddg_region,
    #     safesearch="moderate",
    #     time=None,
    #     size=None,
    #     color=None,
    #     type_image=None,
    #     layout=None,
    #     license_image=None,
    #     max_results=None,
    #     page=1,
    #     output=None,
    #     download=False,
    # )

    return Response(resp, status=status.HTTP_200_OK)
