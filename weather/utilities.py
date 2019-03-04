import pprint

from ambient_api.ambientapi import AmbientAPI
from dateutil.parser import parse
from django.utils import timezone

from firefox.utilities import convert_keys
from weather.models import WeatherStation, WeatherData


def get_weather():
    WeatherData.objects.all().delete()
    weather = AmbientAPI()
    devices = weather.get_devices()
    for device in devices:
        try:
            station = WeatherStation.objects.get(mac_address=device.mac_address)

        except WeatherStation.DoesNotExist:
            station = WeatherStation.objects.create(
                name=device.info.get('name'),
                location=device.info.get('location'),
                mac_address=device.mac_address
            )

        if station.enabled:

            current_conditions = convert_keys(device.last_data)
            parsed_date = parse(current_conditions['date'])
            print(parsed_date.tzinfo())
            print(parsed_date)
            current_conditions['date'] = parsed_date
            current_conditions['station'] = station

            try:
                current_data = WeatherData.objects.get(
                    station=station,
                    date=current_conditions.get('date')
                )
            except WeatherData.DoesNotExist:
                current_data = WeatherData.objects.create(**current_conditions)

        for past_data in device.get_data():
            past_data = convert_keys(past_data)
            past_data['station'] = station
            past_data['date'] = timezone.localtime(parse(past_data['date']))
            try:
                past_entry = WeatherData.objects.get(
                    station=station,
                    date=past_data.get('date')
                )
            except WeatherData.DoesNotExist:
                past_entry = WeatherData.objects.create(**past_data)
