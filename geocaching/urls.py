from django.urls import path, re_path

from geocaching.views import ShowCachesView, ShowCacheView

urlpatterns = [
    path("", ShowCachesView.as_view(), name="show_caches"),
    re_path(r"^(?P<name>GC[A-Za-z0-9]+)/$", ShowCacheView.as_view(), name="show_cache"),
]
