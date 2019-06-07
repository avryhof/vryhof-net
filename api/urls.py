from django.conf.urls import url

from api.views import get_zipcodes_in_radius

urlpatterns = [
    url(
        r"^radius.json/(?P<zip_code>\d+)/(?P<radius>[0-9\.]+)/(?P<distance_units>[a-zA-Z]+)/$",
        get_zipcodes_in_radius,
        name="get_zipcodes_in_radius",
    )
]
