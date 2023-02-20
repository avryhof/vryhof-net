import datetime

from django.conf import settings

from livechat.devices.location.device import GeoIP
from livechat.personal_assistant.assistant_skill_class import AssistantSkill
from livechat.utilities.timedate import AwareDateTime
from livechat.utilities.utility_functions import is_empty


class DateSkill(AssistantSkill):
    name = "Date Skill"
    utterances = [
        "what is the date",
        "what date is it",
        "what is today's date",
        "what is today",
    ]

    location = None
    now = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_empty(self.chat_session):
            self.location = self.chat_session.geo

        else:
            self.log("Updating Location")
            self.location = GeoIP()
            setattr(settings, "LOCATION", self.location)

        if not is_empty(self.location):
            self.location.get_location()
            self.now = self.location.get_local_time()

        else:
            self.now = AwareDateTime(datetime.datetime.now(), settings.TIME_ZONE)

    def dom_word(self):
        dom_parts = []

        dom_str = self.now.strftime("%d")
        dom = int(dom_str)

        if dom == 10:
            dom_parts.append("tenth")

        elif dom == 20:
            dom_parts.append("twentieth")

        elif dom_parts == 30:
            dom_parts.append("thirtieth")

        elif dom > 19:
            tens_place = int(dom_str[0])
            dom = int(dom_str[1])

            if tens_place == 2:
                dom_parts.append("twenty")

            elif tens_place == 3:
                dom_parts.append("thirty")

        if dom == 1:
            dom_parts.append("first")
        if dom == 2:
            return "second"
        if dom == 3:
            return "third"
        if dom == 4:
            return "fourth"
        if dom == 5:
            return "fifth"
        if dom == 6:
            return "sixth"
        if dom == 7:
            return "seventh"
        if dom == 8:
            return "eighth"
        if dom == 9:
            return "ninth"
        if dom == 10:
            return "tenth"
        if dom == 11:
            dom_parts.append("eleventh")
        if dom == 12:
            return "twelfth"
        if dom == 13:
            return "thirteenth"
        if dom == 14:
            return "fourteenth"
        if dom == 15:
            return "fifteenth"
        if dom == 16:
            return "sixteenth"
        if dom == 17:
            return "seventeenth"
        if dom == 18:
            return "eightteenh"
        if dom == 19:
            return "nineteenth"

        return " ".join(dom_parts)

    def handle(self):
        dow = self.now.strftime("%A")
        month = self.now.strftime("%B")
        dom = self.dom_word()
        century = self.now.strftime("%Y")[0:2]
        year = self.now.strftime("%Y")[2:4]

        phrase = f"{dow}, {month} {self.now.day}, {century}{year}"
        self.log("Saying: {}".format(phrase))

        return phrase


class LocationSkill(AssistantSkill):
    name = "Location Skill"
    utterances = [
        "where am I",
        "where are we",
        "what is this location",
        "what is the location",
        "what city are we in",
        "what city am I in",
        "what town are we in",
        "what town am I in",
    ]

    location = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_empty(self.chat_session):
            self.location = self.chat_session.geo

        else:
            self.log("Updating Location")
            self.location = GeoIP()
            setattr(settings, "LOCATION", self.location)

        self.location.get_location()

    def handle(self):
        phrase = f"{self.location.city}, {self.location.state} {self.location.zip_code}"

        self.log("Saying: {}".format(phrase))

        return phrase


class TimeSkill(AssistantSkill):
    name = "Time Skill"
    utterances = ["what is the time", "what time is it"]

    location = None
    now = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_empty(self.chat_session):
            self.location = self.chat_session.geo

        else:
            self.log("Updating Location")
            self.location = GeoIP()
            setattr(settings, "LOCATION", self.location)

        if not is_empty(self.location):
            self.location.get_location()
            self.now = self.location.get_local_time()

        else:
            self.now = AwareDateTime(datetime.datetime.now(), settings.TIME_ZONE)

    def handle(self):
        hour = self.now.hour
        if hour > 12:
            hour = hour - 12

        minute = self.now.minute
        ap = self.now.strftime("%p")

        phrase = "{}:{} {}".format(hour, str(minute).zfill(2), ap)
        self.log("Saying: {}".format(phrase))

        return phrase


class TimeZoneSkill(AssistantSkill):
    name = "TimeZone Skill"
    utterances = [
        "what is the time zone",
        "what is the timezone",
        "what timezone am I in",
        "what time zone am I in",
        "what is the local timezone"
        "what is the local time zone"
    ]

    location = None
    now = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_empty(self.chat_session):
            self.location = self.chat_session.geo

        else:
            self.log("Updating Location")
            self.location = GeoIP()
            setattr(settings, "LOCATION", self.location)

        if not is_empty(self.location):
            self.location.get_location()
            self.now = self.location.get_local_time()

        else:
            self.now = AwareDateTime(datetime.datetime.now(), settings.TIME_ZONE)

    def handle(self):
        phrase = self.location.time_zone
        self.log("Saying: {}".format(phrase))

        return phrase


class WeatherSkill(AssistantSkill):
    name = "Weather Skill"
    utterances = [
        "what is the weather",
    ]

    location = None
    now = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not is_empty(self.chat_session):
            self.location = self.chat_session.geo

        else:
            self.log("Updating Location")
            self.location = GeoIP()
            setattr(settings, "LOCATION", self.location)

        if not is_empty(self.location):
            self.location.get_location()
            self.now = self.location.get_local_time()

        else:
            self.now = AwareDateTime(datetime.datetime.now(), settings.TIME_ZONE)

    def handle(self):
        weather = settings.LOCATION.get_weather()
        phrase = (
            f"The current conditions are {weather.description} "
            f"and {int(round(weather.temperature__ferenheight, 0))} degrees. "
            f"The wind is {weather.wind_direction__words} "
            f"at {int(round(weather.wind_speed__mph, 0))} miles per hour."
        )

        self.log("Saying: {}".format(phrase))

        return phrase
