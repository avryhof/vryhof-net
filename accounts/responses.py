from rest_framework import status
from rest_framework.response import Response

ERROR_KEY = "error"
ERROR_DESCRIPTION_KEY = "error_description"
ERROR_URI_KEY = "error_uri"

INVALID_REQUEST_MESSAGE = "invalid_request"
INVALID_CLIENT_MESSAGE = "invalid_client"
INVALID_GRANT_MESSAGE = "invalid_grant"
INVALID_SCOPE_MESSAGE = "invalid_scope"

RESULT_KEY = "result"

NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Expires": 0,
    "Pragma": "no-cache",
}

UNAUTHORIZED_CLIENT_MESSAGE = "unauthorized_client"
UNAUTHORIZED_USER_MESSAGE = "unauthorized_user"
UNSUPPORTED_GRANT_TYPE_MESSAGE = "unsupported_grant_type"


def SuccessResponse(data):
    return Response(data, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)


def SuccessMessageResponse(message):
    return SuccessResponse({RESULT_KEY: message})


def ErrorMessageResponse(message):
    return SuccessResponse({ERROR_KEY: message})


def BadRequestResponse(message):
    return Response(
        {ERROR_KEY: message},
        status=status.HTTP_400_BAD_REQUEST,
        headers=NO_CACHE_HEADERS,
    )


def UnAuthorizedRequestResponse(message):
    return Response({ERROR_KEY: message}, status=status.HTTP_401_UNAUTHORIZED, headers=NO_CACHE_HEADERS)


INVALID_CLIENT_RESPONSE = UnAuthorizedRequestResponse(INVALID_CLIENT_MESSAGE)

INVALID_REQUEST_RESPONSE = BadRequestResponse(INVALID_REQUEST_MESSAGE)

INVALID_GRANT_RESPONSE = Response(
    {ERROR_KEY: INVALID_GRANT_MESSAGE, ERROR_DESCRIPTION_KEY: "The access_token is invalid or expired."},
    status=status.HTTP_401_UNAUTHORIZED,
    headers=NO_CACHE_HEADERS,
)

INVALID_SCOPE_RESPONSE = UnAuthorizedRequestResponse(INVALID_SCOPE_MESSAGE)

UNAUTHORIZED_USER_RESPONSE = UnAuthorizedRequestResponse(UNAUTHORIZED_USER_MESSAGE)

UNAUTHORIZED_CLIENT_RESPONSE = UnAuthorizedRequestResponse(UNAUTHORIZED_CLIENT_MESSAGE)

UNSUPPORTED_GRANT_TYPE_RESPONSE = BadRequestResponse(UNSUPPORTED_GRANT_TYPE_MESSAGE)

UNKNOWN_ERROR_RESPONSE = BadRequestResponse("unknown_error")


def ServerErrorResponse(data):
    return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE, headers=NO_CACHE_HEADERS)
