from django.conf.urls import url

from assistant.views import parse_text, intent_responder

urlpatterns = [
    url(r"^parse/$", parse_text, name="parse_text"),
    url(r"^intent/$", intent_responder, name="intent"),
]
