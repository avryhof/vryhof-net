from django.conf import settings
from django.db import models


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
