from django.conf import settings
from django.db.models import (
    TextField,
    CharField,
    Model,
    FloatField,
    DateTimeField,
    BigIntegerField,
    IntegerField,
    BooleanField,
    ForeignKey,
    DO_NOTHING,
    DecimalField,
    DateField)


class WeatherStation(Model):
    enabled = BooleanField(default=True)
    name = TextField(null=True)
    cwop_name = CharField(max_length=64, null=True)
    weather_underground_id = CharField(max_length=100, null=True)
    location = CharField(max_length=255, null=True)
    mac_address = CharField(max_length=17, null=True)
    latitude = DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = DecimalField(max_digits=9, decimal_places=6, null=True)

    def __str__(self):
        return "%s@%s" % (self.name, self.mac_address)


class WeatherData(Model):
    station = ForeignKey(WeatherStation, null=True, on_delete=DO_NOTHING)
    baromabsin = FloatField(null=True)
    baromrelin = FloatField(null=True)
    dailyrainin = FloatField(null=True)
    local_date = DateTimeField(null=True)
    tz = CharField(max_length=128, default=settings.TIME_ZONE)
    date = DateTimeField(null=True)
    dateutc = BigIntegerField(null=True)
    dew_point = FloatField(null=True)
    eventrainin = FloatField(null=True)
    feels_like = FloatField(null=True)
    feels_likein = FloatField(null=True)
    hourlyrainin = FloatField(null=True)
    humidity = IntegerField(null=True)
    humidityin = IntegerField(null=True)
    last_rain = DateTimeField(null=True)
    maxdailygust = FloatField(null=True)
    monthlyrainin = FloatField(null=True)
    solarradiation = FloatField(null=True)
    tempf = FloatField(null=True)
    tempinf = FloatField(null=True)
    totalrainin = FloatField(null=True)
    uv = IntegerField(null=True)
    weeklyrainin = FloatField(null=True)
    winddir = IntegerField(null=True)
    windgustmph = FloatField(null=True)
    windspeedmph = FloatField(null=True)
    windspdmph_avg10m = FloatField(null=True)

    class Meta:
        verbose_name = "Weather Data"
        verbose_name_plural = "Data Points"
        ordering = ["-date"]
        get_latest_by = "date"

    def __str__(self):
        return "%s on %s" % (self.station.name, str(self.date))


class WeatherImages(Model):
    added = DateTimeField(auto_now_add=True)
    date = DateField(null=True)
    time = DateTimeField(null=True)
    filename = CharField(max_length=100, blank=True, null=True)
    path = TextField(null=True)
    url = TextField(null=True)

    class Meta:
        verbose_name = "Weather Image"
        verbose_name_plural = "Weather Images"
        ordering = ["-time"]
        get_latest_by = "time"
