import datetime
import decimal
import hashlib
import json
from functools import cmp_to_key
from operator import itemgetter

import requests
from dateutil.parser import parse
from django.utils.timezone import make_aware

from utilities.debugging import log_message
from utilities.python3_compatibility import python3_cmp


def aware_now():
    return make_aware(datetime.datetime.now())


def calc_average(value_list):
    total = sum(value_list)
    count = len(value_list)
    if total > 0 and count > 0:
        return total / count
    else:
        return 0


def calc_percent(value, whole):
    if value > 0 and whole > 0:
        return round((value / whole) * 100, 2)
    else:
        return 0


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]

    else:
        ip = request.META.get("REMOTE_ADDR")

    if "127.0.0.1" in ip:
        req = requests.get("https://api.ipify.org/?format=text")
        ip = req.text

    return ip


def now():
    return make_aware(datetime.datetime.now())


def md5(s, raw_output=False):
    """Calculates the md5 hash of a given string"""
    if isinstance(s, str):
        res = hashlib.md5(s.encode())
    else:
        res = hashlib.md5(s)
    if raw_output:
        return res.digest()
    return res.hexdigest()


def multikeysort(items, columns):
    comparers = [
        ((itemgetter(col[1:].strip()), -1) if col.startswith("-") else (itemgetter(col.strip()), 1)) for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (python3_cmp(fn(left), fn(right)) * mult for fn, mult in comparers)
        return next((result for result in comparer_iter if result), 0)

    return sorted(items, key=cmp_to_key(comparer))


def bool_from_str(value):
    val = None
    if isinstance(value, str):
        val = value.strip().upper()

    if val in ["N", "", None]:
        retn = False

    elif val in ["Y", "X"]:
        retn = True

    return retn


def make_bool(value, **kwargs):
    return_string = kwargs.get("return_string", False)

    retn = None

    if isinstance(value, bool):
        retn = value

    elif isinstance(value, str):
        value = value.lower()

        retn = value in ["true", "t", "y", "yes", "1"]

    elif isinstance(value, int):
        retn = value == 1

    elif value is None:
        retn = False

    if return_string:
        retn = "true" if retn else "false"

    return retn


def int_or_none(value):
    retn = None

    if value is not None:
        try:
            retn = int(value)

        except ValueError:
            retn = None

    return retn


def float_value(value, default=None):
    retn = default

    if value is not None:
        try:
            retn = float(value)
        except:
            retn = default

    return retn


def any_false(iterable):
    for elem in iterable:
        if not elem:
            return True
    return False


def has_required(*args):
    # Determines if at least one of the values passed in is not False(ish)
    retn = False

    for arg in args:
        if arg:
            retn = True
            break

    return retn


def decimal_or_null(value):
    if isinstance(value, str):
        value = value.strip()

    try:
        value = decimal.Decimal(value)

    except:
        value = None

    return value


def split_or_null(value, **kwargs):
    retn = None

    delimiter = kwargs.get("delimiter", " ")

    if isinstance(value, str):

        retn = value.split(delimiter)

        # Don't return a list with an empty first element.
        if len(retn) == 1 and retn[0] == "":
            retn = None

    return retn


def string_or_none(value):
    retn = None

    if value and value != "":
        try:
            retn = str(value).strip()
        except:
            retn = None

    return retn


def timestamp_or_none(value):
    retn = None

    if value:
        try:
            retn = parse(value)
        except:
            retn = None

    return retn


def term_search(string_to_search, search_terms):
    contains_term = False
    if not string_to_search or not search_terms:
        contains_term = False
    else:
        search_terms = make_list(search_terms)
        for search_term in search_terms:
            if search_term in string_to_search.lower():
                contains_term = True
                break

    return contains_term


def aware_date_or_none(value):
    if value is not None:
        try:
            retn = make_aware(value)
        except (AttributeError, ValueError):
            retn = value

    return retn if value is not None else None


def date_or_none(value):
    retn = None

    if value:
        try:
            new_value = "%s-%s-%s" % (value[0:4], value[4:6], value[6:8])
        except IndexError:
            pass
        except Exception as e:
            log_message(e)
        else:
            retn = timestamp_or_none(new_value)

    return retn


def to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict))


def make_list(thing_that_should_be_a_list):
    """If it is not a list.  Make it one. Return a list."""
    if thing_that_should_be_a_list is None:
        thing_that_should_be_a_list = []

    if not isinstance(thing_that_should_be_a_list, list):
        thing_that_should_be_a_list = [thing_that_should_be_a_list]

    return thing_that_should_be_a_list


def uuid_value(uuid_string):
    junk1, retn, junk3 = uuid_string.split("'")

    return retn


def years_ago(years=18, end_date=False):
    if not end_date:
        end_date = datetime.datetime.now()
    today = end_date.isoformat()[0:10]
    today_year, today_month, today_day = today.split("-")
    start_year = int(today_year) - years

    return datetime.datetime(year=start_year, month=int(today_month), day=int(today_day))


def is_empty(value):
    return value in [False, None, "", {}, [], ()]
