import base64
import logging

logger = logging.getLogger(__name__)


def strip_padding(value):
    try:
        padding_char = "=".encode()
        unpadded_input = value.rstrip(padding_char)
    except TypeError:
        padding_char = "="
        unpadded_input = value.rstrip(padding_char)

    return unpadded_input


def unstrip_padding(value):
    padding_char = "="

    if value is not None:
        input_length = len(value)
        padding_length = 4 - (input_length % 4)

        if padding_length > 0:
            value = "%s%s" % (value, padding_char * padding_length)

    return value


def b64encode(input):
    if isinstance(input, str):
        input = input.encode()

    input = base64.urlsafe_b64encode(input).decode().rstrip("=")

    return input.encode()


def b64decode(input):
    if isinstance(input, bytes):
        input = input.decode()

    padded_input = input + '=='

    if isinstance(input, str):
        padded_input = padded_input.encode()

    # padded_input = input.ljust(ceil(len(input) / 4) * 4, "=")
    return base64.urlsafe_b64decode(padded_input)
