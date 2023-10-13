from django.urls import path

from poi.views import ShowCachesView, ShowCacheView

urlpatterns = [
    path("geocaches/", ShowCachesView.as_view(), name="geocaches"),
    path("geocaches/<str:name>/", ShowCacheView.as_view(), name="show_cache"),
]
