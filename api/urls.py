from django.urls import path

from api.views import get_zipcodes_in_radius, zipcode_to_geoname

urlpatterns = [
    path(
        "radius.json/<str:zip_code>/<str:radius>/<str:distance_units>/",
        get_zipcodes_in_radius,
        name="get_zipcodes_in_radius",
    ),
    path("zipcode-to-geonameid/<str:zip_code>/", zipcode_to_geoname, name="zip-to-geo")
]
