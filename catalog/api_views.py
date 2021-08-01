import datetime

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from assistant.api_auth import AnonymousAuthentication
from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AnonymousPermission
from catalog.models import CatalogVariant, Catalog


@api_view(["POST"])
@authentication_classes((AnonymousAuthentication,))
@permission_classes((AnonymousPermission,))
def rfid_lookup(request):
    catalog_id = request.data.get("catalog_id", 1)
    rfid_id = request.data.get("rfid_id")

    try:
        catalog_variant = CatalogVariant.objects.get(rfid_id=rfid_id)
    except CatalogVariant.DoesNotExist:
        catalog_variant = CatalogVariant.objects.create(rfid_id=rfid_id, name="Item for RFID: {}".format(rfid_id))
        resp = catalog_variant.as_dict()
        resp.update(message="Item Created")
    else:
        resp = catalog_variant.as_dict()

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)
