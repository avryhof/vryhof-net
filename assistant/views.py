import json
from operator import itemgetter

from Levenshtein._levenshtein import distance
from phonetisch import soundex
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ssml_builder.core import Speech

from alexa.models import LanguageModel
from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AuthorizedAgentPermission
from assistant.utility_functions import request_to_dict

speech = Speech()


@api_view(['GET', 'POST'])
@permission_classes((AuthorizedAgentPermission,))
def parse_text(request):
    """
    Traverses the language model and compares samples using soundex and Levenshtein distance of the interpreted text.
    :param request:
    :return:
    """

    data = request_to_dict(request)
    text = data.get('text')

    try:
        interaction_model = LanguageModel.objects.get(enabled=True)

    except LanguageModel.DoesNotExist:
        resp = {
            '_text': text
        }

    else:
        text_soundex = soundex.encode_word(text)
        simple_text = text.strip().replace(' ', '').lower()

        matches = []

        for intent in interaction_model.intents.filter(enabled=True):

            for sample in intent.samples:
                sample_soundex = soundex.encode_word(sample)
                word_distance = distance(text, sample)

                simple_sample = sample.strip().replace(' ', '').lower()

                if text_soundex == sample_soundex:
                    matches.append({
                        'distance': 0,
                        'intent': intent.name,
                        'sample': sample
                    })

                elif simple_text in simple_sample:
                    matches.append({
                        'distance': 1,
                        'intent': intent.name,
                        'sample': sample
                    })

                else:
                    if word_distance < 10:
                        matches.append({
                            'distance': word_distance,
                            'intent': intent.name,
                            'sample': sample
                        })

        matches = sorted(matches, key=itemgetter('distance'))

        if len(matches) > 0 and matches[0].get('distance') < 5:
            closest_match = matches[0]

        else:
            closest_match = None

        resp = {
            '_text': text,
            # 'closest_match': closest_match,
            'intent': closest_match.get('intent') if closest_match else closest_match,
            # 'matches': matches
        }

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)