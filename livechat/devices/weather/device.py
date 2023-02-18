import asyncio
import pprint

import aiohttp
import pynws
from django.conf import settings

from livechat.devices.weather import constants
from livechat.personal_assistant.base_class import BaseClass


def celsius_to_ferenheight(value):
    return value * 1.8 + 32


def kph_to_mph(value):
    return value * 0.6214


def kph_to_knots(value):
    return value * 0.53996


class Weather(BaseClass):
    coordinates = ()

    temperature = 0
    wind_chill = 0
    dewpoint = 0
    description = None
    wind_direction = 0
    wind_direction_abbr = ""
    wind_speed = 0
    gust = 0

    def __init__(self, latitude, longitude, **kwargs):
        super().__init__(**kwargs)

        self.coordinates = (latitude, longitude)

        try:
            loop = asyncio.get_event_loop()
        except Exception as e:
            loop = asyncio.new_event_loop()

        loop.run_until_complete(self.get_nws())

    def __getattr__(self, item):
        """
        Returns an attribute value if it directly exists.

        If not; split to attribute and conversion function, then returns the output
        from the conversion function.
        ex: .temperature__ferenheight -> self.fetenheight(self.temperature)
        """
        try:
            return object.__getattribute__(self, item)
        except Exception as e:
            try:
                item_name, item_unit = item.split("__")
                item_val = object.__getattribute__(self, item_name)
            except Exception as e:
                self.log(e)
            else:
                try:
                    item_unit_func = object.__getattribute__(self, item_unit)
                except Exception as e:
                    self.log(e)
                else:
                    return item_unit_func(item_val)

        return f"{item} not found."

    def ferenheight(self, value) -> float:
        """
        Converts celsius to ferenheight (most temperatures from NWS are in celsius)
        """
        return celsius_to_ferenheight(value)

    def mph(self, value) -> float:
        """
        Converts kph to mph (most speeds from NWS are in kph)
        """
        return kph_to_mph(value)

    def knots(self, value) -> float:
        """
        Converts kph to knots (most speeds from NWS are in kph)
        """
        return kph_to_knots(value)

    def direction_abbr(self, value) -> str:
        """
        Converts a wind direction from degrees to cardinal abbreviation
        ex: 140 = SSE
        """
        for k, v in constants.WIND_DIRECTIONS.items():
            minimum, maximum = sorted(v)
            if minimum <= value <= maximum:
                return k

    def words(self, direction) -> str:
        """
        Converts a wind direction from degrees, or the cardinal abbreviation to words.
        ex: 140 = SSE = South South East

        """
        if isinstance(direction, str):
            direction_str = direction
        else:
            direction_str = self.direction_abbr(direction)
        return " ".join([constants.DIRECTIONS.get(x) for x in direction_str])

    async def get_nws(self):
        loc = self.coordinates
        userid = getattr(settings, "NWS_EMAIL")

        async with aiohttp.ClientSession() as session:
            nws = pynws.SimpleNWS(*loc, userid, session)
            await nws.set_station()
            await nws.update_observation()
            # await nws.update_forecast()
            # await nws.update_alerts_forecast_zone()
            # pprint.pprint(nws.observation)
            # print(nws.forecast[0])
            # print(nws.alerts_forecast_zone)

            self.temperature = nws.observation.get("temperature")
            self.wind_chill = nws.observation.get("windChill")
            self.dewpoint = nws.observation.get("dewpoint")
            self.description = nws.observation.get("textDescription")
            self.wind_direction = nws.observation.get("windDirection")
            self.wind_speed = nws.observation.get("windSpeed")
            self.gust = nws.observation.get("windGust")
