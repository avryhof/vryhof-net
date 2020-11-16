import datetime
import inspect
import logging
import math
import os
import pprint
import sys

logger = logging.getLogger(__name__)


def calc_percent(x, y):
    return round(((x * 100) / y), 2)


def log_message(message, **kwargs):
    pretty = kwargs.get("pretty", False)
    log_output_processors = kwargs.get("log_output", [logger.error])
    output_processors = kwargs.get("output", [])
    write_stdout = kwargs.get("stdout", False)

    if write_stdout:
        output_processors.append(sys.stdout.write)

    if pretty:
        message = pprint.pformat(message)

    debug_timestamp = datetime.datetime.now().isoformat()[0:19]
    debug_filename = os.path.basename(inspect.stack()[1][1])
    debug_function_name = inspect.stack()[1][3]
    debug_line_number = inspect.stack()[1][2]

    message = "%s - %s (%s):\n%s" % (debug_filename, debug_function_name, debug_line_number, message)

    for output_processor in output_processors:
        output_processor("%s: %s\n\n" % (debug_timestamp, message))

    for log_output_processor in log_output_processors:
        log_output_processor(message)


def time_diff_seconds(start_time, end_time):
    return (end_time - start_time).total_seconds()


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


def timer(init_time=False):
    if not init_time:
        init_time = datetime.datetime.now()
        log_message("Command initiated.")
        return init_time
    else:
        log_message("Command completed.")

        complete_time = datetime.datetime.now()
        command_total_seconds = time_diff_seconds(init_time, complete_time)
        log_message("Command took %s to run." % time_in_words(command_total_seconds))


def verbose_time(total_seconds):
    command_hours = 0
    command_minutes = math.floor(total_seconds / 60)
    command_seconds = total_seconds - (command_minutes * 60)

    if command_minutes > 60:
        command_hours = math.floor(command_minutes / 60)
        command_minutes = command_minutes - (command_hours * 60)

    retn = dict(hours=command_hours, minutes=command_minutes, seconds=command_seconds)

    return retn
