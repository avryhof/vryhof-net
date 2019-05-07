from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ssml_builder.core import Speech

from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AuthorizedAgentPermission

speech = Speech()


@api_view(['GET', 'POST'])
@permission_classes((AuthorizedAgentPermission,))
def parse_text(request):
    text = request.data.get('text')

    resp = {
        '_text': text
    }

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)
