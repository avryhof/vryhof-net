# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from weather.models import WeatherData, WeatherStation, WeatherImages
from weather.utilities import get_weather, translate_datetime, translate_date


class WeatherView(TemplateView):
    extra_css = ["css/weather.css"]
    extra_javascript = []

    template_name = "weather.html"
    name = "Weather"

    request = None

    def get_context_data(self, **kwargs):
        context = super(WeatherView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        get_weather()

        weather_stations = []

        for station in WeatherStation.objects.all():
            weatherdata = {"tempf": "--"}

            try:
                weatherdata = WeatherData.objects.filter(station=station).latest()
            except WeatherData.DoesNotExist:
                pass

            weather_stations.append({"station": station, "data": weatherdata})

        context["weather_stations"] = weather_stations

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(WeatherView, self).dispatch(*args, **kwargs)


def weather_image(request, *args, **kwargs):
    date = kwargs.get('date', False)
    time = kwargs.get('time', False)

    search_dict = dict()

    if time:
        search_dict.update(dict(time=translate_datetime(date, time)))

    elif not time and date:
        search_dict.update(dict(date=translate_date(date)))

    return_images = WeatherImages.objects.filter(**search_dict)

    if len(return_images) > 0:
        return_image = return_images[0]
        imagefile = open(return_image.path, 'rb')

        response = HttpResponse(
            content=imagefile,
            content_type='image/jpeg'
        )
        response['Cache-Control'] = 'no-cache'
    else:
        response = HttpResponse(status=404)
        response.status_code = 404

    return response
