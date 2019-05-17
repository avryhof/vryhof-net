from django.conf.urls import url

from weather.views import WeatherView

urlpatterns = [url(r"^$", WeatherView.as_view(), name="firefox_home")]
