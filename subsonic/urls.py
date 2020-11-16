from django.urls import path

from subsonic.views import intent_responder, stream_song

urlpatterns = [
    path("", intent_responder, name="subsonic-intent-responder"),
    path("stream/<str:song_id>/", stream_song, name="subsonic-stream"),
]
