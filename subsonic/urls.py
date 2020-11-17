from django.urls import path

from subsonic.views import intent_responder, stream_song, cover_art

urlpatterns = [
    path("", intent_responder, name="subsonic-intent-responder"),
    path("stream/<str:song_id>/", stream_song, name="subsonic-stream"),
    path("cover/<str:song_id>/", cover_art, name="subsonic-cover"),
]
