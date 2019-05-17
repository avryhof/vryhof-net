import json
import os

from django.conf import settings
from django.utils.text import slugify


def rebuild_interaction_model(interaction_model):
    default_intents = [
        {"name": "AMAZON.YesIntent", "samples": []},
        {"name": "AMAZON.NoIntent", "samples": []},
        {"name": "AMAZON.HelpIntent", "samples": []},
        {"name": "AMAZON.StopIntent", "samples": []},
        {"name": "AMAZON.CancelIntent", "samples": []},
        {"name": "AMAZON.FallbackIntent", "samples": []},
    ]

    intents = []

    try:
        for intent in interaction_model.intents.all():
            intents.append(
                {"name": intent.name, "slots": [], "samples": intent.samples}
            )
    except TypeError:
        print("Failure")
        pass

    else:
        for intent in default_intents:
            do_add = True
            for my_intent in intents:
                if my_intent.get("name") == intent.get("name"):
                    do_add = False
            if do_add:
                intents.append(intent)

        alexa_model = {
            "interactionModel": {
                "languageModel": {
                    "invocationName": interaction_model.invocation_name.lower(),
                    "intents": intents,
                    "types": [],
                }
            }
        }

        filename = "%s-interaction-model.json" % slugify(
            interaction_model.invocation_name
        )

        im = open(os.path.join(settings.BASE_DIR, "alexa", "json", filename), "w")
        json.dump(alexa_model, im)
        im.close()
