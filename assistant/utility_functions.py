import json
import sys

from ssml_builder.core import Speech

from assistant.constants import API_V1

speech = Speech()


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
