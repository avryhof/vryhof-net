import json
import re
import sys
from operator import itemgetter

from Levenshtein._levenshtein import distance
from past.builtins import unicode
from phonetisch import soundex
from ssml_builder.core import Speech

from assistant.constants import API_V1

speech = Speech()


def search_model(input_value, **kwargs):
    model = kwargs.get('model', False)
    field = kwargs.get('field', False)
    filter_args = kwargs.get('filter', False)

    closest_match = None

    if isinstance(input_value, (str, unicode)) and model and field:
        text_soundex = soundex.encode_word(input_value)
        simple_text = re.sub('[^A-Za-z0-9]', '', input_value).strip().replace(' ', '').lower()

        if filter_args:
            model_items = model.objects.filter(**filter_args)
        else:
            model_items = model.objects.all()

        matches = []

        for item in model_items:
            field_value = getattr(item, field, '')

            field_soundex = soundex.encode_word(field_value)
            simple_field_text = re.sub('[^A-Za-z0-9]', '', field_value).strip().replace(' ', '').lower()
            word_distance = distance(input_value, field_value)

            if text_soundex == field_soundex:
                matches.append({
                    'distance': 0,
                    'item': item
                })

            elif simple_text in simple_field_text:
                matches.append({
                    'distance': 1,
                    'item': item
                })

            else:
                if word_distance < 10:
                    matches.append({
                        'distance': word_distance,
                        'item': item
                    })

            matches = sorted(matches, key=itemgetter('distance'))

            if len(matches) > 0 and matches[0].get('distance') < 5:
                closest_match = matches[0]

    return closest_match.get('item')


def request_to_dict(request):
    if isinstance(request.data, str):
        data = json.loads(request.data)

    elif isinstance(request.data, dict):
        data = request.data

    else:
        data = {}

    return data


def intent_response(text, app_name):
    ssml = ''

    if isinstance(text, str):
        ssml = speech.say(text)

    resp = {
        'body': {
            'version': API_V1,
            'response': {
                'outputSpeech': {
                    'type': 'SSML',
                    'ssml': ssml.speak()
                },
                'card': {
                    'type': 'Simple',
                    'title': app_name,
                    'content': text
                },
                'shouldEndSession': False,
                'type': '_DEFAULT_RESPONSE'
            },
            'sessionAttributes': {},
            'userAgent': 'python-assistant/0.0.1 Python/%i.%i.%i' % (
                sys.version_info[0], sys.version_info[1], sys.version_info[2])
        }
    }

    return resp
