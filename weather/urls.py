from django.conf.urls import url

from weather.views import WeatherView, weather_image

urlpatterns = [
    url(r"^image.jpg$", weather_image, name="weather_image"),
    url(r"^(?P<date>\d{4}\d{2}\d{2})/image.jpg$", weather_image, name="weather_image_date"),
    url(r"^(?P<date>\d{8})/(?P<time>\d{6})/image.jpg$", weather_image, name="weather_image_time"),
    url(r"^$", WeatherView.as_view(), name="firefox_home")
]
