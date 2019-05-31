from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AuthorizedAgentPermission
from assistant.utility_functions import request_to_dict
from mail.models import MailMessage


@api_view(["GET", "POST"])
@permission_classes((AuthorizedAgentPermission,))
def parse_email(request):
    """
    Just dump whatever was posted into the database.
    :param request:
    :return:
    """

    data = request_to_dict(request)

    MailMessage.objects.create(message=data)

    resp = {}

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)
