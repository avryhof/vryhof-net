import datetime
import random

from alexa.models import BedtimeStory
from weather.models import WeatherStation, WeatherData


def get_story(**kwargs):
    story_title = kwargs.get('story_title', False)

    speech_text = 'No stories found.'

    story = None
    
    if not story_title:
        all_stories = set(BedtimeStory.objects.filter(enabled=True))

        if len(all_stories) > 0:
            random_stories = random.sample(all_stories, 1)
            story = random.choice(random_stories)

    else:
        try:
            story = BedtimeStory.objects.get(enabled=True, title__icontains=story_title)

        except BedtimeStory.DoesNotExist:
            pass

    if story:
        speech_text = '%s. %s' % (story.title, story.story)

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
