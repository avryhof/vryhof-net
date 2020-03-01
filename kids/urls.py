from django.urls import path

from kids.view import KidSitesView

urlpatterns = [path("", KidSitesView.as_view(), name="kids_home")]
