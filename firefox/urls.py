from django.conf.urls import url

from firefox.views import FirefoxHomeView

urlpatterns = [url(r"^$", FirefoxHomeView.as_view(), name="firefox_home")]
