import calendar
import datetime

import dateutil
import holidays
import pytz
from dateutil.parser import parse

ATOM = "Y-m-d\tH:i:sP"
COOKIE = "l, d-M-Y H:i:s T"
ISO8601 = "Y-m-d\tH:i:sO"
ISO8601_EXPANDED = "X-m-d\tH:i:sP"
RFC822 = "D, d M y H:i:s O"
RFC850 = "l, d-M-y H:i:s T"
RFC1036 = "D, d M y H:i:s O"
RFC1123 = "D, d M Y H:i:s O"
RFC7231 = "D, d M Y H:i:s GMT"
RFC2822 = "D, d M Y H:i:s O"
RFC3339 = "Y-m-d\tH:i:sP"
RFC3339_EXTENDED = "Y-m-d\tH:i:s.vP"
RSS = "D, d M Y H:i:s O"
W3C = "Y-m-d\tH:i:sP"


class DateFormat:
    value = datetime.datetime.now()
    iso = value.isocalendar()
    timezone = value.tzinfo

    iso_date = "%Y-%m-%d"
    iso_time = "%H:%M:%S"
    rfc_date = "%a, %d %b"

    replacements = {
        "d": "%d",
        "D": "%a",
        "l": "%A",
        "w": "%w",
        "F": "%B",
        "m": "%m",
        "M": "%b",
        "y": "%y",
        "Y": "%Y",
        "A": "%p",
        "h": "%I",
        "H": "%H",
        "i": "%M",
        "s": "%S",
        "u": "%f",
        "e": "%Z",
        "O": "%z",
    }

    int_replacements = {
        "j": "%d",
        "z": "%j",
        "n": "%m",
        "g": "%I",
        "G": "%H"
    }

    def __init__(self, value=datetime.datetime.now()):
        self.value = value
        self.iso = value.isocalendar()
        self.timezone = value.tzinfo

    def __getattr__(self, item):
        if item in self.replacements.keys():
            return self.value.strftime(self.replacements.get(item))
        elif item in self.int_replacements.keys():
            return str(int(self.value.strftime(self.replacements.get(item))))
        elif item in ["P"]:
            return self.value.strftime("%p").upper()
        elif hasattr(self, item):
            return getattr(self, item)
        else:
            return str(item)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def format(self, format_token):
        return "".join([self.get(x) for x in format_token])

    @property
    def N(self):
        return str(self.value.strftime("%w") + 1)

    @property
    def S(self):
        if self.value.day in (11, 12, 13):  # Special case
            return "th"
        last = self.value.day % 10
        if last == 1:
            return "st"
        if last == 2:
            return "nd"
        if last == 3:
            return "rd"
        return "th"

    @property
    def t(self):
        return str(calendar.monthrange(self.data.year, self.data.month)[1]).zfill(2)

    @property
    def L(self):
        return calendar.isleap(self.value.year)

    @property
    def o(self):
        return self.iso[0]

    @property
    def I(self):
        return '1' if self.timezone.dst(self.data) else '0'

    @property
    def P(self):
        if self.value.minute == 0 and self.value.hour == 0:
            return "midnight"
        elif self.value.minute == 0 and self.value.hour == 12:
            return "noon"
        else:
            return " ".join([self.f, self.a])

    @property
    def T(self):
        try:
            return self.timezone.tzname(self.value)
        except Exception:
            return self.O

    @property
    def Z(self):
        offset = self.timezone.utcoffset(self.value)
        return offset.days * 86400 + offset.seconds

    @property
    def c(self):
        return self.value.isoformat()

    @property
    def r(self):
        return self.value.strftime("%a, %d %b %Y %H:%M:%S %z")

    @property
    def u(self):
        return self.value.microsecond

    @property
    def U(self):
        return int(calendar.timegm(self.value.utctimetuple()))


class AwareDateTime(object):
    tzinfo = pytz.utc
    now = datetime.datetime.utcnow().replace(tzinfo=tzinfo)
    value = now

    def __init__(self, value=datetime.datetime.now(), tzinfo="UTC"):
        if isinstance(value, str):
            self.value = parse(value)

        if isinstance(tzinfo, str):
            self.tzinfo = dateutil.tz.gettz(tzinfo)
        elif isinstance(tzinfo, datetime.tzinfo):
            self.tzinfo = tzinfo

        self.make_aware()

    def __getattr__(self, item):
        return getattr(self.value, item)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def make_aware(self):
        if self.value.utcoffset() is None or self.timezone != self.tzinfo:
            self.value = self.value.astimezone(self.tzinfo)

    def day_of_week(self) -> str:
        return self.value.strftime("%A")

    def format(self, format_string="r") -> str:
        if "%" in format_string:
            return self.value.strftime(format_string)
        else:
            df = DateFormat(self.value)
            return df.format(format_string)

    @property
    def business_day(self) -> bool:
        return not self.is_holiday and self.weekday

    @property
    def end_of_day(self):
        return self.value.replace(hour=23, minute=59, second=59)

    @property
    def is_holiday(self) -> bool:
        holiday_object = getattr(holidays, "US")
        holiday_dict = holiday_object(years=self.value.year)
        return self.value.date() in list(holiday_dict.keys())

    @property
    def next_business_day(self):
        next_day = self.next_day
        while not next_day.business_day:
            next_day = next_day.next_day

        return next_day

    @property
    def next_day(self):
        return AwareDateTime(self.value + datetime.timedelta(days=1))

    @property
    def offset(self) -> int:
        return int(self.value.strftime("%z"))

    @property
    def previous_business_day(self):
        previous = self.previous_day
        while not previous.business_day:
            previous = previous.previous_day

        return previous

    @property
    def previous_day(self):
        return AwareDateTime(self.value - datetime.timedelta(days=1))

    @property
    def start_of_day(self):
        return self.value.replace(hour=0, minute=0, second=0)

    @property
    def timezone(self) -> str:
        return self.value.strftime("%Z")

    @property
    def week_of_month(self) -> int:
        return int(self.value.isocalendar()[1] - self.value.replace(day=1).isocalendar()[1] + 1)

    @property
    def week_of_year(self) -> int:
        return int(self.value.strftime("%W"))

    @property
    def weekday(self) -> bool:
        return not self.weekend

    @property
    def weekend(self) -> bool:
        return self.day_of_week().lower() in ["saturday", "sunday"]


def aware_now():
    # A simple way of getting an aware datetime object of the current datetime
    dt = AwareDateTime()

    return dt.now
