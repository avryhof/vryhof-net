import json
import pprint

import requests
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        data = {
            "handler": {"name": "make_query"},
            "intent": {
                "name": "make_query",
                "params": {
                    "song": {
                        "original": "the sound of silence",
                        "resolved": "the sound of silence",
                    }
                },
                "query": "Ask Sub sonic to play the sound of silence",
            },
            "scene": {
                "name": "actions.scene.START_CONVERSATION",
                "slotFillingStatus": "UNSPECIFIED",
                "slots": {},
                "next": {"name": "actions.scene.END_CONVERSATION"},
            },
            "session": {
                "id": "ABwppHE1zS5eI1_qk8UowHwZyLdnZaTGRiBj0EqCal1Bn8r5oqZ4WBIYaZFalJSXyhT7ken6ucehHWDXDQ0",
                "params": {},
                "typeOverrides": [],
                "languageCode": "",
            },
            "user": {
                "locale": "en-US",
                "params": {},
                "accountLinkingStatus": "ACCOUNT_LINKING_STATUS_UNSPECIFIED",
                "verificationStatus": "VERIFIED",
                "packageEntitlements": [],
                "lastSeenTime": "2020-11-14T23:43:21Z",
            },
            "home": {"params": {}},
            "device": {"capabilities": ["SPEECH", "RICH_RESPONSE", "LONG_FORM_AUDIO"]},
        }

        # data = {
        #     "handler": {"name": "make_query"},
        #     "intent": {
        #         "name": "make_query",
        #         "params": {
        #             "action": {"original": "play", "resolved": "Play"},
        #             "song": {
        #                 "original": "the sound of silence by disturbed",
        #                 "resolved": "the sound of silence by disturbed",
        #             },
        #         },
        #         "query": "ask sub sonic to play the song the sound of silence by disturbed",
        #     },
        #     "scene": {
        #         "name": "actions.scene.START_CONVERSATION",
        #         "slotFillingStatus": "UNSPECIFIED",
        #         "slots": {},
        #         "next": {"name": "actions.scene.END_CONVERSATION"},
        #     },
        #     "session": {
        #         "id": "ABwppHEjZ45WtRMVSkrkdupmV6HHsNGNuqQsPgvsAGJmOlJWtXWKxBAkdRyayz7Zt7GomCYc27GmFwjPYYU",
        #         "params": {},
        #         "typeOverrides": [],
        #         "languageCode": "",
        #     },
        #     "user": {
        #         "locale": "en-US",
        #         "params": {},
        #         "accountLinkingStatus": "ACCOUNT_LINKING_STATUS_UNSPECIFIED",
        #         "verificationStatus": "VERIFIED",
        #         "packageEntitlements": [],
        #         "lastSeenTime": "2020-11-15T00:42:42Z",
        #     },
        #     "home": {"params": {}},
        #     "device": {"capabilities": ["SPEECH", "RICH_RESPONSE", "LONG_FORM_AUDIO"]},
        # }

        # data = {
        #     "handler": {"name": "make_query"},
        #     "intent": {
        #         "name": "make_query",
        #         "params": {
        #             "action": {"original": "shuffle", "resolved": "Shuffle"},
        #             "artist": {"original": "enya", "resolved": "enya"},
        #         },
        #         "query": "ask sub sonic to shuffle songs by enya",
        #     },
        #     "scene": {
        #         "name": "actions.scene.START_CONVERSATION",
        #         "slotFillingStatus": "UNSPECIFIED",
        #         "slots": {},
        #         "next": {"name": "actions.scene.END_CONVERSATION"},
        #     },
        #     "session": {
        #         "id": "ABwppHE3_kCnWzY50Jga2sNVgAoQiEfvCK1sraO-fZLF6QFh1_HU16v7ecq7PmzNa3CiE48eKE_f0uZQ4OI",
        #         "params": {},
        #         "typeOverrides": [],
        #         "languageCode": "",
        #     },
        #     "user": {
        #         "locale": "en-US",
        #         "params": {},
        #         "accountLinkingStatus": "ACCOUNT_LINKING_STATUS_UNSPECIFIED",
        #         "verificationStatus": "VERIFIED",
        #         "packageEntitlements": [],
        #         "lastSeenTime": "2020-11-15T00:48:13Z",
        #     },
        #     "home": {"params": {}},
        #     "device": {"capabilities": ["SPEECH", "RICH_RESPONSE", "LONG_FORM_AUDIO"]},
        # }

        data_string = json.dumps(data)

        # resp = requests.post(url="https://alexa.vryhof.net/subsonic/", json=data, verify=True)
        resp = requests.post(url="http://127.0.0.1:8000/subsonic/", json=data)

        # print(resp.headers)
        try:
            pprint.pprint(resp.json())
        except Exception:
            print(resp.text)
