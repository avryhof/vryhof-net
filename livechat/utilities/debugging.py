import datetime
import inspect
import logging
import math
import os
import pprint
import sys

from django.conf import settings

logger = logging.getLogger(__name__)


def log_message(message, **kwargs):
    pretty = kwargs.get("pretty", False)

    if pretty:
        message = pprint.pformat(message)

    debug_timestamp = datetime.datetime.now().isoformat()[0:19]
    debug_filename = os.path.basename(inspect.stack()[1][1])
    debug_function_name = inspect.stack()[1][3]
    debug_line_number = inspect.stack()[1][2]

    message = "%s - %s (%s):\n%s" % (debug_filename, debug_function_name, debug_line_number, message)

    if settings.DEBUG:
        sys.stdout.write("%s: %s\n\n" % (debug_timestamp, message))
    else:
        logger.error(message)


def calc_percent(x, y):
    return round(((x * 100) / y), 2)


def time_diff_seconds(start_time, end_time):
    return (end_time - start_time).total_seconds()


def verbose_time(total_seconds):
    command_hours = 0
    command_minutes = math.floor(total_seconds / 60)
    command_seconds = total_seconds - (command_minutes * 60)

    if command_minutes > 60:
        command_hours = math.floor(command_minutes / 60)
        command_minutes = command_minutes - (command_hours * 60)

    retn = dict(hours=command_hours, minutes=command_minutes, seconds=command_seconds)

    return retn


def time_in_words(total_seconds):
    time_dict = verbose_time(total_seconds)

    time_parts = []
    if time_dict["hours"] > 0:
        time_parts.append("%i hours" % time_dict["hours"])
    if time_dict["minutes"] > 0:
        time_parts.append("%i minutes" % time_dict["minutes"])
    if time_dict["seconds"] > 0:
        time_parts.append("%i seconds" % time_dict["seconds"])

    return ", ".join(time_parts)
