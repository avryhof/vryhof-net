from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.response import Response

from assistant.api_auth import AnonymousAuthentication
from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AnonymousPermission
from subsonic.google_responses import GoogleResponse
from subsonic.subsonic_class import Subsonic


@api_view(["POST"])
@authentication_classes((AnonymousAuthentication,))
@permission_classes((AnonymousPermission,))
def intent_responder(request):
    resp = {}

    # log_message(type(request.data))
    # log_message(request.data)

    intent = request.data.get("intent", {})

    query = intent.get("query")
    params = intent.get("params")
    session = request.data.get("session")

    # print(query)
    # pprint.pprint(params)

    action = "Play"
    artist = False
    song = False
    genre = False
    song_type = False

    if "action" in params:
        action = params.get("action", {}).get("resolved")

    if "artist" in params:
        artist = params.get("artist", {}).get("resolved")

    if "song" in params:
        song = params.get("song", {}).get("resolved")

    if "song_type" in params:
        song_type = params.get("song_type", {}).get("resolved")

    if "genre" in params:
        genre = params.get("genre", {}).get("resolved")

    google_resp = GoogleResponse(session, request)
    if action == "Shuffle":
        if artist:
            resp = google_resp.random_song_by_artist(artist)
        elif genre:
            resp = google_resp.song_by_genre(genre)
        else:
            resp = google_resp.random_song()

    elif action == "Play":
        if song and not artist and "by" in song.lower():
            parts = song.lower().split("by")
            artist = parts[-1]
            song = "by".join(parts[0:-1])

        if song_type == "next":
            resp = google_resp.next_song()
        elif song_type == "random":
            resp = google_resp.random_song()
        elif song and artist:
            resp = google_resp.search(song, artist)
        elif song and not artist:
            resp = google_resp.search(song)
        elif genre:
            resp = google_resp.song_by_genre(genre)

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)


def stream_song(request, *args, **kwargs):
    song_id = kwargs.get("song_id")

    ss = Subsonic()
    song = ss.get_song(song_id)
    songstream = ss.download(song_id)

    file_name = song.get("path").split("/")[-1]

    response = HttpResponse(content=songstream, content_type=song.get("contentType"))
    response["Content-Disposition"] = "attachment; filename={}".format(file_name)

    return response


# def cover_art(request, *args, **kwargs):
#     song_id = kwargs.get("song_id")
#
#     ss = Subsonic()
#     song = ss.get_song(song_id)
#     cover = ss.get_cover_art(song_id)
#
#     response = HttpResponse(content=songstream, content_type=song.get("contentType"))
#     response["Content-Disposition"] = "attachment; filename={}".format(file_name)
#
#     return response
