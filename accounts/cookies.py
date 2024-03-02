import datetime
import logging
from base64 import b64encode
from http.cookies import CookieError

from django.conf import settings
from django.core import signing
from django.core.signing import Signer

from accounts.base64safe import strip_padding, unstrip_padding, b64decode

logger = logging.getLogger(__name__)


def string_bytes_to_string(value):
    if isinstance(value, str) and value[0:2] == "b'":
        value = value[2:-1]

    return value


def decode_value(value):
    """First binary 64 decodes a value, cryptographically un-signs it and then binary 64 decodes it again.  This undoes
    what encode_value does."""
    signer = Signer()

    original = None

    if isinstance(value, bytes):
        value = value.decode()

    decoded_value = b64decode(value)
    decoded_value = string_bytes_to_string(decoded_value)
    signed_value = decoded_value.decode()

    try:
        original = signer.unsign(signed_value)
    except signing.BadSignature:
        print("Tampering detected!")

    return original


def encode_value(original_value):
    """First binary 64 encodes a value, cryptographically signs it and then 64 encodes it one last time.  Use
    decode_value to read values encoded with this function."""
    signer = Signer()

    value = signer.sign(original_value)
    return_value = b64encode(value.encode())

    return return_value


def get_cookie_in_request(request, key):
    """Get the value of a given key in a signed cookie, if present and not expired, else None"""
    key = encode_value(key)
    if not isinstance(key, str):
        key = key.decode("utf-8")

    key = strip_padding(key)

    cookie_salt = getattr(settings, "COOKIE_SALT", settings.SECRET_KEY)

    try:
        cookie_value = request.get_signed_cookie(key, default=None, salt=cookie_salt)
    except Exception:
        if key:
            key = unstrip_padding(key)
        cookie_value = request.get_signed_cookie(key, default=None, salt=cookie_salt)

    if cookie_value:
        cookie_value = decode_value(cookie_value)

    return cookie_value


def set_cookie_in_response(response, key, value, days_expire=120):
    """Sets a cookie that will expired in the days_expire time else by default in 120 days"""

    max_age = days_expire * 24 * 60 * 60
    expire_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age)
    expires = expire_date.strftime(getattr(settings, "COOKIE_DATE_FORMAT", "%a, %d-%m-%Y %H:%M:%S EST"))

    key = encode_value(key)
    value = encode_value(value)

    key = key.decode()
    value = value.decode("utf-8")

    try:
        response.set_signed_cookie(
            key,
            value,
            salt=getattr(settings, "COOKIE_SALT", settings.SECRET_KEY),
            max_age=max_age,
            expires=expires,
            domain=getattr(settings, "SESSION_COOKIE_DOMAIN"),
            secure=getattr(settings, "SESSION_COOKIE_SECURE", None),
        )
    except CookieError:
        logger.info("Cookie error encountered. Stripping padding")

        key = strip_padding(key)
        value = strip_padding(value)
        response.set_signed_cookie(
            key,
            value,
            salt=getattr(settings, "COOKIE_SALT", settings.SECRET_KEY),
            max_age=max_age,
            expires=expires,
            domain=getattr(settings, "SESSION_COOKIE_DOMAIN"),
            secure=getattr(settings, "SESSION_COOKIE_SECURE", None),
        )

    return response
