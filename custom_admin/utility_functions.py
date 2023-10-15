import bleach as bleach
import datetime
import inspect
import json
import logging
import os
import pprint
import re
import sys
import traceback
from collections import OrderedDict
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import formats
from django.utils.timezone import make_aware

from custom_admin.models import ExceptionLog

logger = logging.getLogger(__name__)


def aware_now():
    return make_aware(datetime.datetime.now())


def clean_api_dict(input_value) -> dict:
    if isinstance(input_value, OrderedDict):
        input_value = to_dict(input_value)

    return convert_keys(clean_api_results(input_value))


def clean_api_results(api_result, **kwargs):
    """
    This function will accept, a list, dictionary, or string.
    If a list or dictionary is provided, it will recursively traverse through it, and run bleach on all string values.
    If a string is provided, it will bleach that string.
    Any other data type is simply returned as-is.

    :param input_dict:
    :return:
    """
    retn = None

    if isinstance(api_result, str):
        retn = bleach.clean(api_result)

    elif isinstance(api_result, dict):
        retn = {}

        for k, v in api_result.items():

            if isinstance(v, str):
                retn[k] = bleach.clean(v)

            else:
                retn[k] = clean_api_results(v)

    elif isinstance(api_result, list):
        retn = []

        for list_item in api_result:
            if isinstance(list_item, str):

                retn.append(bleach.clean(list_item))

            elif isinstance(list_item, dict) or isinstance(list_item, list):

                retn.append(clean_api_results(list_item))

            else:
                retn.append(list_item)

    else:
        retn = api_result

    return retn


def convert_keys(input_value):
    """
    Convert all of the keys in a dict recursively from CamelCase to snake_case.
    Also strips leading and trailing whitespace from string values.
    :param input_value:
    :return:
    """
    retn = None

    if isinstance(input_value, list):
        retn = []
        for list_item in input_value:
            if isinstance(list_item, (dict, list)):
                retn.append(convert_keys(list_item))
            else:
                if isinstance(list_item, str):
                    retn.append(list_item.strip())

                else:
                    retn.append(list_item)

    elif isinstance(input_value, dict):
        retn = dict()
        for k, v in input_value.items():
            new_key_s = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", k)
            new_key = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", new_key_s).lower()
            if isinstance(v, (dict, list)):
                retn[new_key] = convert_keys(v)

            else:
                if isinstance(v, str):
                    retn[new_key] = v.strip()
                else:
                    retn[new_key] = v

    return retn


def format_date(input_date, **kwargs):
    """
    Assumes a U.S. Date format, and converts it to or from a standardized date format. (YYYY-MM-DD)
    :param input_date:
    :param kwargs:
    :return:
    """
    reverse = kwargs.get("reverse", False)
    time_object = kwargs.get("return_datetime", False)

    retn = ""

    if not input_date:
        input_date = datetime.datetime.now()

    if isinstance(input_date, dict):
        retn = format_dates(input_date)

    elif isinstance(input_date, str) or isinstance(input_date, str):
        month = None
        day = None
        year = None

        if "/" in input_date:
            try:
                month, day, year = input_date.split("/")
            except ValueError:
                pass

        elif "-" in input_date:
            try:
                year, month, day = input_date[0:10].split("-")
            except ValueError:
                print(input_date)

        elif len(input_date) == 8:
            year = input_date[0:4]
            month = input_date[4:6]
            day = input_date[6:8]

        if month and day and year:
            month = int(month)
            day = int(day)
            year = int(year)

            if year < 1900:
                year = year + 2000

            input_date = datetime.date(year=year, month=month, day=day)

    if isinstance(input_date, datetime.datetime) or isinstance(input_date, datetime.date):
        if time_object:
            retn = input_date

        else:
            retn = input_date.isoformat()[0:10]

    return retn


def format_dates(input_dict, **kwargs):
    """
    Format all items in a dict that have the word date in their key to YYYY-MM-DD format
    :param input_dict:
    :return:
    """
    retn = {}

    for k, v in list(input_dict.items()):
        if "date" in k:
            retn[k] = format_date(v, **kwargs)

        elif isinstance(v, list):
            retn[k] = format_dates_list(v)

        elif isinstance(v, dict):
            retn[k] = format_dates(v, **kwargs)

        else:
            retn[k] = v

    return retn


def format_dates_list(input_list, **kwargs):
    """
    Format all items in a list of dicts that have the word date in their key to YYYY-MM-DD format
    :param input_list:
    :return:
    """
    retn_list = []

    for list_item in input_list:
        if isinstance(list_item, dict):
            retn_list.append(format_dates(list_item, **kwargs))
        elif isinstance(list_item, list):
            retn_list.append(format_dates_list(list_item, **kwargs))
        else:
            retn_list.append(list_item)

    return retn_list


def is_empty(value):
    return value in [0, "", None, False, {}, [], ()]


def log_message(message, **kwargs):
    pretty = kwargs.get("pretty", False)
    ip_address = kwargs.get("ip_address", False)
    return_value = kwargs.get("return_value", False)

    retn = None
    if return_value:
        retn = message

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
        message = "%s - %s (%s):\n%s" % (debug_filename, debug_function_name, debug_line_number, message)

    if settings.DEBUG:
        sys.stdout.write("%s: %s\n\n" % (debug_timestamp, message))

    else:
        logger.error(message)

    if return_value:
        return retn


def log_exception(request_or_user, exception_object, **kwargs):
    debug_filename = os.path.basename(inspect.stack()[1][1])
    debug_function_name = inspect.stack()[1][3]
    debug_line_number = inspect.stack()[1][2]

    try:
        exception_url = request_or_user.build_absolute_uri()
    except Exception as e:
        user = request_or_user
        exception_url = None
    else:
        user = request_or_user.user

        if isinstance(user, AnonymousUser):
            user = None
            exception_url = None

    try:
        ExceptionLog.objects.create(
            user=user,
            exception=exception_object,
            traceback=traceback.format_exc(),
            message=kwargs.get("message", None),
            path=exception_url,
            filename=debug_filename,
            function_name=debug_function_name,
            line_number=debug_line_number,
        )
    except Exception as e:
        log_message("Error creating Exception Log: {} - For exception: {}".format(e, exception_object))


def make_list(thing_that_should_be_a_list) -> list:
    """If it is not a list.  Make it one. Return a list."""
    if thing_that_should_be_a_list is None:
        thing_that_should_be_a_list = []

    if not isinstance(thing_that_should_be_a_list, list):
        thing_that_should_be_a_list = [thing_that_should_be_a_list]

    return thing_that_should_be_a_list


def php_date(value, arg):
    return formats.date_format(value, arg)


def quick_clean(data):
    return convert_keys(clean_api_results(data))


def to_dict(input_ordered_dict) -> dict:
    return json.loads(json.dumps(input_ordered_dict))
