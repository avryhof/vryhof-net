import datetime
import inspect
import logging
import os
import pprint
import random
import string
import sys

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.timezone import make_aware

logger = logging.getLogger(__name__)


def aware_now():
    return make_aware(datetime.datetime.now())


def is_empty(value):
    return value in [0, False, None, "", {}, []]


def not_empty(value):
    return not is_empty(value)


def random_password():
    valid_chars = string.ascii_letters + string.digits
    length = random.randint(32, 64)

    return "".join(random.choice(valid_chars) for i in range(length))


def load_model(app_name, model_name=None):
    if is_empty(model_name):
        accessor = app_name
        model_name = accessor.split(".")[-1]
    else:
        accessor = ".".join([app_name, model_name])

    try:
        return django_apps.get_model(accessor, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            f"{accessor} must be of the form 'app_label.model_name'"
        )

    except LookupError:
        raise ImproperlyConfigured(
            f"{accessor} refers to model '{model_name}' that has not been installed"
        )


def log_message(message, **kwargs):
    pretty = kwargs.get("pretty", False)
    ip_address = kwargs.get("ip_address", False)

    if pretty:
        message = pprint.pformat(message)

    debug_timestamp = datetime.datetime.now().isoformat()[0:19]
    debug_filename = os.path.basename(inspect.stack()[1][1])
    debug_function_name = inspect.stack()[1][3]
    debug_line_number = inspect.stack()[1][2]

    if ip_address:
        message = "%s: %s - %s (%s):\n%s" % (
            ip_address,
            debug_filename,
            debug_function_name,
            debug_line_number,
            message,
        )
    else:
        message = "%s - %s (%s):\n%s" % (
            debug_filename,
            debug_function_name,
            debug_line_number,
            message,
        )

    if settings.DEBUG:
        sys.stdout.write("%s: %s\n\n" % (debug_timestamp, message))

    logger.error(message)
