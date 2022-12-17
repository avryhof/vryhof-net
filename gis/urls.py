from django.urls import path

from gis.views import get_zipcodes_in_radius

urlpatterns = [
    path(
        "zip-code/<str:zip_code>/<str:radius>/<str:distance_units>/",
        get_zipcodes_in_radius,
        name="get_zipcodes_in_radius",
    )
]
