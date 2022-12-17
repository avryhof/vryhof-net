from django.urls import path

from geocaching.views import ShowCachesView, ShowCacheView

urlpatterns = [
    path("", ShowCachesView.as_view(), name="geocaches"),
    path("<str:name>/", ShowCacheView.as_view(), name="show_cache"),
]
