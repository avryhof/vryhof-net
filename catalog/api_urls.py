from django.urls import path

from catalog.api_views import rfid_lookup

urlpatterns = [path("rfid/", rfid_lookup, name="rfid-lookup")]
