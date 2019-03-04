from django.db.models import TextField, CharField, Model, FloatField, DateTimeField, BigIntegerField, IntegerField, \
    BooleanField, ForeignKey, DO_NOTHING


class WeatherStation(Model):
    enabled = BooleanField(default=True)
    name = TextField(null=True)
    location = CharField(max_length=255, null=True)
    mac_address = CharField(max_length=17, null=True)

    def __str__(self):
        return '%s@%s' % (self.name, self.mac_address)


class WeatherData(Model):
    station = ForeignKey(WeatherStation, null=True, on_delete=DO_NOTHING)
    baromabsin = FloatField(null=True)
    baromrelin = FloatField(null=True)
    dailyrainin = FloatField(null=True)
    date = DateTimeField(null=True)
    dateutc = BigIntegerField(null=True)
    dew_point = FloatField(null=True)
    eventrainin = FloatField(null=True)
    feels_like = FloatField(null=True)
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

    class Meta:
        verbose_name = 'Weather Data'
        verbose_name_plural = 'Data Points'
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return '%s on %s' % (self.station.name, str(self.date))
