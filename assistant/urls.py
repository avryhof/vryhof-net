from django.conf.urls import url

from assistant.views import parse_text

urlpatterns = [
    url(r'^parse/$', parse_text, name='parse_text'),
]