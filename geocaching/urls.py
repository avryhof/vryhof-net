from django.conf.urls import url

from geocaching.views import ShowCachesView, ShowCacheView

urlpatterns = [
    url(r"^$", ShowCachesView.as_view(), name="show_caches"),
    url(r"^(?P<name>GC[A-Za-z0-9]+)/$", ShowCacheView.as_view(), name="show_cache")
]
