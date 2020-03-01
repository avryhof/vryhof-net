from django.urls import path

from assistant.views import parse_text, intent_responder

urlpatterns = [path("parse/", parse_text, name="parse_text"), path("intent/", intent_responder, name="intent")]
