import http.client
import json

from django.conf import settings
from django.db import models

from gis.models import AbstractStreetAddress
from utilities.utility_functions import strip_trailing_zeroes


class WeatherStation(models.Model):
    enabled = models.BooleanField(default=True)
    name = models.TextField(null=True)
    cwop_name = models.CharField(max_length=64, null=True)
    weather_underground_id = models.CharField(max_length=100, null=True)
    location = models.CharField(max_length=255, null=True)
    mac_address = models.CharField(max_length=17, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    def __str__(self):
        return "%s@%s" % (self.name, self.mac_address)

    @property
    def nws_lat(self):
        return strip_trailing_zeroes(str(round(self.latitude, 4)))

    @property
    def nws_lng(self):
        return strip_trailing_zeroes(str(round(self.longitude, 4)))

    @property
    def nws_point_id(self):
        return f"https://{NWSPoint.base_url()}/points/{self.nws_lat},{self.nws_lng}"

    @property
    def nws_point(self):
        return NWSPoint.objects.get(id=self.nws_point_id)



class WeatherData(models.Model):
    station = models.ForeignKey(WeatherStation, null=True, on_delete=models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    baromabsin = models.FloatField(null=True)
    baromrelin = models.FloatField(null=True)
    dailyrainin = models.FloatField(null=True)
    local_date = models.DateTimeField(null=True)
    tz = models.CharField(max_length=128, default=settings.TIME_ZONE)
    date = models.DateTimeField(null=True)
    dateutc = models.BigIntegerField(null=True)
    dew_point = models.FloatField(null=True)
    dew_pointin = models.FloatField(null=True)
    eventrainin = models.FloatField(null=True)
    feels_like = models.FloatField(null=True)
    feels_likein = models.FloatField(null=True)
    hourlyrainin = models.FloatField(null=True)
    humidity = models.IntegerField(null=True)
    humidityin = models.IntegerField(null=True)
    last_rain = models.DateTimeField(null=True)
    maxdailygust = models.FloatField(null=True)
    monthlyrainin = models.FloatField(null=True)
    solarradiation = models.FloatField(null=True)
    tempf = models.FloatField(null=True)
    tempinf = models.FloatField(null=True)
    totalrainin = models.FloatField(null=True)
    uv = models.IntegerField(null=True)
    weeklyrainin = models.FloatField(null=True)
    winddir = models.IntegerField(null=True)
    windgustmph = models.FloatField(null=True)
    windspeedmph = models.FloatField(null=True)
    windspdmph_avg10m = models.FloatField(null=True)
    batt_co2 = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Weather Data"
        verbose_name_plural = "Data Points"
        ordering = ["-date"]
        get_latest_by = "date"

    def __str__(self):
        return "%s on %s" % (self.station.name, str(self.date))


class WeatherImages(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    date = models.DateField(null=True)
    time = models.DateTimeField(null=True)
    filename = models.CharField(max_length=100, blank=True, null=True)
    path = models.TextField(null=True)
    url = models.TextField(null=True)

    class Meta:
        verbose_name = "Weather Image"
        verbose_name_plural = "Weather Images"
        ordering = ["-time"]
        get_latest_by = "time"


class NWSPoint(AbstractStreetAddress):
    id = models.URLField(primary_key=True)
    grid_id = models.CharField(max_length=10, null=True)
    grid_x = models.IntegerField(null=True)
    grid_y = models.IntegerField(null=True)
    radar_station = models.CharField(max_length=10, null=True)

    @classmethod
    def base_url(cls):
        return "api.weather.gov"

    @classmethod
    def client(cls):
        return http.client.HTTPSConnection(cls.base_url())

    @classmethod
    def get_point_data(cls, latitude, longitude):
        latitude = float(latitude)
        longitude = float(longitude)

        lat = strip_trailing_zeroes(str(round(latitude, 4)))
        lng = strip_trailing_zeroes(str(round(longitude, 4)))

        conn = cls.client()
        headers = {"User-Agent": "Python / HTTP Client"}
        conn.request("GET", f"/points/{lat},{lng}", headers=headers)
        res = conn.getresponse()
        data = res.read()

        return json.loads(data.decode("utf-8"))

    def call(self, url):
        conn = self.client()
        headers = {"User-Agent": "Python / HTTP Client"}
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read()

        return json.loads(data.decode("utf-8"))

    @property
    def point_data_url(self):
        return f"/points/{self.latitude},{self.longitude}"

    @property
    def point_data(self):
        return self.__class__.get_point_data(self.latitude, self.longitude)

    @property
    def grid_url(self):
        return f"/gridpoints/{self.grid_id}/{self.grid_x},{self.grid_y}"

    @property
    def forecast(self):
        return self.call(f"{self.grid_url}/forecast")

    @property
    def forecast_data(self):
        return NWSForecast.objects.filter(point=self).order_by("start_time")

    @property
    def forecast_hourly_url(self):
        return f"{self.grid_url}/forecast/hourly"

    @property
    def forecast_grid_data_url(self):
        return f"{self.grid_url}"

    @property
    def observation_stations_url(self):
        return f"{self.grid_url}/stations"


class NWSForecast(models.Model):
    point = models.ForeignKey(NWSPoint, null=True, on_delete=models.CASCADE)
    day_name = models.CharField(max_length=20, null=True)
    day_number = models.IntegerField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    icon = models.URLField(null=True)
    is_daytime = models.BooleanField(default=True)
    dewpoint_unit = models.CharField(max_length=20, null=True)
    dewpoint_value = models.FloatField(null=True)
    precipitation_probability_unit = models.CharField(max_length=20, null=True)
    precipitation_probability_value = models.CharField(max_length=20, null=True)
    relative_humidity_unit = models.CharField(max_length=20, null=True)
    relative_humidity_value = models.FloatField(null=True)
    temperature_unit = models.CharField(max_length=20, null=True)
    temperature_value = models.FloatField(null=True)
    temperature_trend = models.CharField(max_length=20, null=True)
    wind_direction = models.CharField(max_length=5, null=True)
    wind_speed = models.CharField(max_length=50, null=True)
    forecast_short = models.TextField(null=True)
    forecast_detailed = models.TextField(null=True)
    updated = models.DateTimeField(null=True)
    generated = models.DateTimeField(null=True)
    elevation_unit = models.CharField(max_length=20, null=True)
    elevation_value = models.FloatField(null=True)

    class Meta:
        verbose_name = "Weather Forecast"
        verbose_name_plural = "Weather Forecasts"
        ordering = ["-start_time"]
        get_latest_by = "start_time"

