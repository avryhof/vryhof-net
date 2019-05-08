import datetime
import random

from alexa.models import BedtimeStory
from weather.models import WeatherStation, WeatherData


def get_story():
    all_stories = set(BedtimeStory.objects.filter(enabled=True))

    speech_text = 'No stories found.'

    if len(all_stories) > 0:
        random_stories = random.sample(all_stories, 1)
        random_story = random.choice(random_stories)

        speech_text = '%s. %s' % (random_story.title, random_story.story)

    return speech_text


def get_weather():
    station = WeatherStation.objects.get(name='KD2OTL')
    weather = WeatherData.objects.filter(station=station).order_by('-date')[0]

    speech_text = '%s says it is %s degrees fahrenheit as of %s on %s.' % (
        station.name,
        weather.tempf,
        datetime.datetime.now().strftime('%I:%M %p'),
        datetime.datetime.now().strftime('%B %d, %Y')
    )

    return speech_text


def launch_request():
    speech_text = "Welcome to the Vryhof family Planner"

    return speech_text
