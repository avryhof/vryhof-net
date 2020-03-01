from django.urls import path

from firefox.views import FirefoxHomeView

urlpatterns = [path("", FirefoxHomeView.as_view(), name="firefox_home")]
