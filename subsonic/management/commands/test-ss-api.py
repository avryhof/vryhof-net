import pprint

from django.core.management import BaseCommand

from subsonic.subsonic_class import Subsonic


class Command(BaseCommand):
    def handle(self, *args, **options):
        ss = Subsonic(debug=True)
        # ss = Subsonic(debug=False)

        # ss.stream("4201")
        ss.get_cover_art("4201")

        # songs = ss.search("the sound of silence", "Disturbed")
        # songs = ss.get_random_songs()
        # songs = ss.search2("enya")
        # pprint.pprint(songs)

        # song = songs[0]
        # pprint.pprint(song)

        # pprint.pprint(ss.get_song(song.get("id")))
        # pprint.pprint(ss.get_album(song.get("albumId")))

        # pprint.pprint(ss.get_genres())
