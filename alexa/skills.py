import datetime
import random

import requests

from alexa.models import BedtimeStory
from assistant.utility_functions import search_model
from weather.models import WeatherStation, WeatherData


def get_song(**kwargs):
    search = kwargs.get("search", False)
    speech_text = "I can't find that song."

    song = None

    if search:
        search_data = dict(format="json", search=search)
        if "by" in search.lower():
            title, artist = search.lower().split("by")
            search_data.update({
                "title": title,
                "artist": artist
            })

        search_url = "https://dev.vryhof.net/music/search/"
        resp = requests.get(search_url, params=search_data)

        results = resp.json()
        song = results[0]

        return song

    return speech_text


def get_story(**kwargs):
    story_title = kwargs.get("story_title", False)

    speech_text = "No stories found."

    story = None

    if not story_title:
        all_stories = set(BedtimeStory.objects.filter(enabled=True))

        if len(all_stories) > 0:
            random_stories = random.sample(all_stories, 1)
            story = random.choice(random_stories)

    else:
        try:
            story = search_model(
                story_title, model=BedtimeStory, field="title", filter={"enabled": True}
            )
            story = BedtimeStory.objects.get(enabled=True, title__icontains=story_title)

        except BedtimeStory.DoesNotExist:
            pass

    if story:
        speech_text = "%s. %s" % (story.title, story.story)

    return speech_text


def get_weather():
    station = WeatherStation.objects.get(name="KD2OTL")
    weather = WeatherData.objects.filter(station=station).order_by("-date")[0]

    speech_text = "%s says it is %s degrees fahrenheit as of %s on %s." % (
        station.name,
        weather.tempf,
        datetime.datetime.now().strftime("%I:%M %p"),
        datetime.datetime.now().strftime("%B %d, %Y"),
    )

    return speech_text


def launch_request():
    speech_text = "Welcome to the Vryhof family Planner"

    return speech_text
