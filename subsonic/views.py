from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response

from assistant.api_auth import AnonymousAuthentication
from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AnonymousPermission
from firefox.utilities import log_message


@api_view(["GET", "POST"])
@authentication_classes((AnonymousAuthentication,))
@permission_classes((AnonymousPermission,))
def intent_responder(request, **kwargs):
    resp = {}

    log_message(request.data)

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)
