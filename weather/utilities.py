import datetime
import pprint
import re

import pytz
from ambient_api.ambientapi import AmbientAPI
from ambient_aprs.ambient_aprs import AmbientAPRS
from dateutil.parser import parse
from django.conf import settings
from django.utils.timezone import make_aware

from firefox.utilities import convert_keys, log_message
from weather.models import WeatherStation, WeatherData

date_pattern = r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})"
time_pattern = r"(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})"


def get_weather():
    weather = AmbientAPI()
    devices = weather.get_devices()

    utc_timezone = pytz.timezone("UTC")
    local_timezone = pytz.timezone(settings.TIME_ZONE)

    for device in devices:
        try:
            station = WeatherStation.objects.get(mac_address=device.mac_address)

        except WeatherStation.DoesNotExist:
            station = WeatherStation.objects.create(
                name=device.info.get("name"), location=device.info.get("location"), mac_address=device.mac_address
            )
            log_message("Weather Station created: %s (%s)" % (station.mac_address, station.name))

        if station.enabled:
            last_data = device.last_data
            current_conditions = convert_keys(last_data)
            parsed_date = parse(current_conditions["date"])

            current_conditions["date"] = parsed_date.astimezone(utc_timezone)
            current_conditions["local_date"] = parsed_date.astimezone(local_timezone)
            current_conditions["station"] = station

            pprint.pprint(current_conditions)

            try:
                current_data = WeatherData.objects.get(station=station, date=current_conditions.get("date"))
            except WeatherData.DoesNotExist:
                try:
                    current_data = WeatherData.objects.create(**current_conditions)
                    log_message(
                        "Current weather data collected on %s from %s (%s)"
                        % (current_data.date, current_data.station.mac_address, current_data.station.name)
                    )
                except TypeError as e:
                    current_data = WeatherData.objects.create(
                        station=station,
                        baromabsin=current_conditions.get("baromabsin"),
                        baromrelin=current_conditions.get("baromrelin"),
                        dailyrainin=current_conditions.get("dailyrainin"),
                        local_date=current_conditions.get("local_date"),
                        date=current_conditions.get("date"),
                        dateutc=current_conditions.get("dateutc"),
                        dew_point=current_conditions.get("dew_point"),
                        eventrainin=current_conditions.get("eventrainin"),
                        feels_like=current_conditions.get("feels_like"),
                        hourlyrainin=current_conditions.get("hourlyrainin"),
                        humidity=current_conditions.get("humidity"),
                        humidityin=current_conditions.get("humidityin"),
                        last_rain=current_conditions.get("last_rain"),
                        maxdailygust=current_conditions.get("maxdailygust"),
                        monthlyrainin=current_conditions.get("monthlyrainin"),
                        solarradiation=current_conditions.get("solarradiation"),
                        tempf=current_conditions.get("tempf"),
                        tempinf=current_conditions.get("tempinf"),
                        totalrainin=current_conditions.get("totalrainin"),
                        uv=current_conditions.get("uv"),
                        weeklyrainin=current_conditions.get("weeklyrainin"),
                        winddir=current_conditions.get("winddir"),
                        windgustmph=current_conditions.get("windgustmph"),
                        windspeedmph=current_conditions.get("windspeedmph"),
                        windspdmph_avg10m=current_conditions.get("windspdmph_avg10m"),
                    )
                    log_message(
                        "Current weather data collected on %s from %s (%s)"
                        % (current_data.date, current_data.station.mac_address, current_data.station.name)
                    )
                    log_message("New field found in data. (%s)" % e)

        for past_data in device.get_data():
            past_data = convert_keys(past_data)
            past_data["station"] = station

            past_date = parse(past_data["date"])

            past_data["date"] = past_date.astimezone(utc_timezone)
            past_data["local_date"] = past_date.astimezone(local_timezone)
            try:
                past_entry = WeatherData.objects.get(station=station, date=past_data.get("date"))
            except WeatherData.DoesNotExist:
                past_entry = WeatherData.objects.create(**past_data)
                log_message(
                    "Past weather data collected for %s from %s (%s)"
                    % (past_entry.date, past_entry.station.mac_address, past_entry.station.name)
                )

        aprs = AmbientAPRS(
            station_id=station.name, latitude=station.latitude, longitude=station.longitude  # 43.131258,  # -76.155028
        )

        weather_data = aprs.get_weather_data(weather_data=last_data)
        packet = aprs.build_packet()
        is_aprs = aprs.send_packet()

        if not is_aprs:
            log_message("APRS Packet failed to send.")
            log_message("%s %s %s" % (aprs.station_id, aprs.address, aprs.position))
            log_message(aprs.packet_data)
            log_message(packet)
            log_message(weather_data)
        else:
            log_message("APRS Packet sent successfully.")


def translate_datetime(date_string, time_string):
    date_parts = re.search(date_pattern, date_string).groups()
    time_parts = re.search(time_pattern, time_string).groups()

    date_time = make_aware(
        datetime.datetime(
            year=int(date_parts[0]),
            month=int(date_parts[1]),
            day=int(date_parts[2]),
            hour=int(time_parts[0]),
            minute=int(time_parts[1]),
            second=int(time_parts[2]),
        )
    )

    return date_time


def translate_date(date_string):
    date_parts = re.search(date_pattern, date_string).groups()
    date = make_aware(datetime.datetime(year=int(date_parts[0]), month=int(date_parts[1]), day=int(date_parts[2])))

    return date


def translate_time(time_string):
    time_parts = re.search(time_pattern, time_string)
    time = make_aware(datetime.time(hour=int(time_parts[0]), minute=int(time_parts[1]), second=int(time_parts[2])))

    return time
