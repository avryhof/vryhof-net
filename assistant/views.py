import logging
from operator import itemgetter

from Levenshtein._levenshtein import distance
from ask_sdk_core.skill_builder import SkillBuilder
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django_ask_sdk.skill_adapter import SkillAdapter
from phonetisch import soundex
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from ssml_builder.core import Speech

from alexa.models import LanguageModel, Intent
from assistant import intents
from assistant.constants import NO_CACHE_HEADERS
from assistant.permissions import AuthorizedAgentPermission
from assistant.utility_functions import request_to_dict, intent_response

logger = logging.getLogger(__name__)

speech = Speech()
sb = SkillBuilder()


@api_view(["GET", "POST"])
@permission_classes((AuthorizedAgentPermission,))
def intent_responder(request):
    """
    Reads an intent request (as sent by Alexa Web services) and responds with an intent response.
    :param request:
    :return:
    """
    resp = {}

    data = request_to_dict(request)

    req = data.get("request", {})
    intent_name = req.get("intent", {}).get("name")

    try:
        intent = Intent.objects.get(name=intent_name)

    except Intent.DoesNotExist:
        resp = {"error": "Intent not found."}
        pass

    else:
        try:
            interaction_model = LanguageModel.objects.get(enabled=True)

        except LanguageModel.DoesNotExist:
            resp = {"error": "Interaction model not found."}
            pass

        else:
            intent_resp = "Intent had no response."

            try:
                intent_resp = getattr(intents, intent.name, "Intent had no response.")
            except:
                pass

            resp = intent_response(
                intent_resp, interaction_model.invocation_name.title()
            )

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)


@api_view(["GET", "POST"])
@permission_classes((AuthorizedAgentPermission,))
def parse_text(request):
    """
    Traverses the language model and compares samples using soundex and Levenshtein distance of the interpreted text.
    :param request:
    :return:
    """

    data = request_to_dict(request)
    text = data.get("text")

    try:
        interaction_model = LanguageModel.objects.get(enabled=True)

    except LanguageModel.DoesNotExist:
        resp = {"_text": text}

    else:
        text_soundex = soundex.encode_word(text)
        simple_text = text.strip().replace(" ", "").lower()

        matches = []

        for intent in interaction_model.intents.filter(enabled=True):

            for sample in intent.samples:
                sample_soundex = soundex.encode_word(sample)
                word_distance = distance(text, sample)

                simple_sample = sample.strip().replace(" ", "").lower()

                if text_soundex == sample_soundex:
                    matches.append(
                        {"distance": 0, "intent": intent.name, "sample": sample}
                    )

                elif simple_text in simple_sample:
                    matches.append(
                        {"distance": 1, "intent": intent.name, "sample": sample}
                    )

                else:
                    if word_distance < 10:
                        matches.append(
                            {
                                "distance": word_distance,
                                "intent": intent.name,
                                "sample": sample,
                            }
                        )

        matches = sorted(matches, key=itemgetter("distance"))

        if len(matches) > 0 and matches[0].get("distance") < 5:
            closest_match = matches[0]

        else:
            closest_match = None

        resp = {
            "_text": text,
            # 'closest_match': closest_match,
            "intent": closest_match.get("intent") if closest_match else closest_match,
            # 'matches': matches
        }

    return Response(resp, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)
