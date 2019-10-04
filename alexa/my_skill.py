# -*- coding: utf-8 -*-

# This is a simple Hello World Alexa Skill, built using
# the decorators approach in skill builder.
import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

from alexa.skills import launch_request, get_weather, get_story, get_song

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

skill_name = "Vryhof Family Planner"


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    speech_text = launch_request()

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .set_should_end_session(False)
        .response
    )


@sb.request_handler(can_handle_func=is_intent_name("GetWeatherIntent"))
def get_weather_intent_handler(handler_input):
    speech_text = get_weather()

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .set_should_end_session(False)
        .response
    )


@sb.request_handler(can_handle_func=is_intent_name("ReadBookIntent"))
def get_story_intent_handler(handler_input):
    speech_text = get_story()

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .set_should_end_session(False)
        .response
    )


@sb.request_handler(can_handle_func=is_intent_name("ReadStoryIntent"))
def read_story_intent_handler(handler_input):
    slots = handler_input.request_envelope.request.intent.slots

    story_title = slots.get("story_title").value
    speech_text = get_story(story_title=story_title)

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .set_should_end_session(False)
        .response
    )


@sb.request_handler(can_handle_func=is_intent_name("PlaySongIntent"))
def play_song_intent_handler(handler_input):
    slots = handler_input.request_envelope.request.intent.slots

    song_title = slots.get("song_search").value
    speech_text = get_song(search=song_title)

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .set_should_end_session(False)
        .response
    )


@sb.request_handler(
    can_handle_func=lambda handler_input: is_intent_name("AMAZON.CancelIntent")(
        handler_input
    )
    or is_intent_name("AMAZON.StopIntent")(handler_input)
)
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    speech_text = "Goodbye!"

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .response
    )


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    speech_text = "I can't help with that."

    return (
        handler_input.response_builder.speak(speech_text)
        .set_card(SimpleCard(skill_name, speech_text))
        .set_should_end_session(False)
        .response
    )


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    return handler_input.response_builder.response


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    logger.error(exception, exc_info=True)

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


skill = sb.create()
