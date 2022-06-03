from django.urls import path

from firefox.views import FirefoxHomeView, SignatureView

urlpatterns = [
    path("", FirefoxHomeView.as_view(), name="firefox_home"),
    path("signature/", SignatureView.as_view(), name="signature"),
]
