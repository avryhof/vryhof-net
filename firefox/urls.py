from django.urls import path

from firefox.views import FirefoxHomeView, SignatureView, SearchView

urlpatterns = [
    path("", FirefoxHomeView.as_view(), name="firefox_home"),
    path("search/", SearchView.as_view(), name="search"),
    path("signature/", SignatureView.as_view(), name="signature"),
]
