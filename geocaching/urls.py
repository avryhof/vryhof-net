from django.conf.urls import url

from geocaching.views import ShowCachesView

urlpatterns = [url(r"^$", ShowCachesView.as_view(), name="show_caches")]
