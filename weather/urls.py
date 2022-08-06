from django.urls import path

from weather.views import WeatherView, weather_image

urlpatterns = [
    path("image.jpg", weather_image, name="weather_image"),
    path("<str:date>/image.jpg", weather_image, name="weather_image_date"),
    path("<str:date>/<str:time>/image.jpg", weather_image, name="weather_image_time"),
    path("", WeatherView.as_view(), name="weather"),
]
