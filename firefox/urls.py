from django.urls import path

from firefox.views import FirefoxHomeView, SignatureView, SearchView, my_ip_address

urlpatterns = [
    path("start/", FirefoxHomeView.as_view(), name="firefox_home"),
    path("search/", SearchView.as_view(), name="search"),
    path("signature/", SignatureView.as_view(), name="signature"),
    path("my-ip-address/", my_ip_address, name="my-ip-address"),
]
