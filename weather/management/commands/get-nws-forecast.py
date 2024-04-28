import pprint

from dateutil.parser import parse
from django.core.management import BaseCommand

from utilities.utility_functions import aware_now
from weather.models import WeatherStation, NWSPoint, NWSForecast


class Command(BaseCommand):
    def handle(self, *args, **options):
        ws = WeatherStation.objects.first()

        try:
            nws_point = NWSPoint.objects.get(id=ws.nws_point_id)
        except NWSPoint.DoesNotExist:
            point_data = NWSPoint.get_point_data(ws.nws_lat, ws.nws_lng)

            nws_point = NWSPoint.objects.create(
                id=ws.nws_point_id,
                latitude=ws.nws_lat,
                longitude=ws.nws_lng,
                grid_id=point_data.get("properties", {}).get("gridId"),
                grid_x=point_data.get("properties", {}).get("gridX"),
                grid_y=point_data.get("properties", {}).get("gridY"),
                radar_station=point_data.get("properties", {}).get("radarStation"),
                city=point_data.get("properties", {})
                .get("relativeLocation", {})
                .get("properties", {})
                .get("city"),
                state=point_data.get("properties", {})
                .get("relativeLocation", {})
                .get("properties", {})
                .get("state"),
            )

            nws_point.link_postal_code()

        forecasts = NWSForecast.objects.filter(point=nws_point).order_by("start_time")

        last_updated = aware_now()
        if forecasts.count() > 0:
            last_updated = forecasts.first().updated

        forecast = nws_point.forecast.get("properties")

        generated = None
        updated = None

        try:
            generated = parse(forecast.get("generatedAt"))
        except TypeError:
            print("generated", forecast.get("generatedAt"))

        try:
            updated = parse(forecast.get("updated"))
        except TypeError:
            print("updated", forecast.get("updated"))

        if forecasts.count() == 0 or updated > last_updated:
            NWSForecast.objects.filter(point=nws_point).delete()

            elevation_unit = forecast.get("elevation", {}).get("unitCode")
            elevation_value = forecast.get("elevation", {}).get("value")

            for period in forecast.get("periods"):
                start_time = parse(period.get("startTime"))
                end_time = parse(period.get("endTime"))

                p = NWSForecast.objects.create(
                    point=nws_point,
                    day_name=period.get("name"),
                    day_number=period.get("number"),
                    start_time=start_time,
                    end_time=end_time,
                    icon=period.get("icon"),
                    is_daytime=period.get("isDaytime"),
                    dewpoint_unit=period.get("dewpoint", {}).get("unitCode"),
                    dewpoint_value=period.get("dewpoint", {}).get("value"),
                    precipitation_probability_unit=period.get(
                        "probabilityOfPrecipitation", {}
                    ).get("unitCode"),
                    precipitation_probability_value=period.get(
                        "probabilityOfPrecipitation", {}
                    ).get("value"),
                    relative_humidity_unit=period.get("relativeHumidity", {}).get(
                        "unitCode"
                    ),
                    relative_humidity_value=period.get("relativeHumidity", {}).get(
                        "value"
                    ),
                    temperature_unit=period.get("temperatureUnit"),
                    temperature_value=period.get("temperature"),
                    temperature_trend=period.get("temperatureTrend"),
                    wind_direction=period.get("windDirection"),
                    wind_speed=period.get("windSpeed"),
                    forecast_short=period.get("shortForecast"),
                    forecast_detailed=period.get("detailedForecast"),
                    elevation_unit=elevation_unit,
                    elevation_value=elevation_value,
                    updated=updated,
                    generated=generated,
                )
