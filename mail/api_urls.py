from django.conf.urls import url

from mail.api_views import parse_email

urlpatterns = [
    url(r"^incoming/$", parse_email, name="parse_email"),
]
