import re

import requests
from django.conf import settings

from utilities.debugging import log_message


class Enrich:
    api_key = None

    # endpoint = "https://api.peopledatalabs.com/v4/person"
    endpoint = "https://api.peopledatalabs.com/v5/person/enrich"

    def __init__(self, **kwargs):
        self.api_key = getattr(settings, "PDL_KEY")

    def _pdl_call(self, params):
        retn = dict()

        call_params = dict()

        base_params = dict(api_key=self.api_key)

        call_params.update(base_params)
        call_params.update(params)

        log_message(self.endpoint)

        resp = requests.get(self.endpoint, params=call_params, verify=True)

        log_message(resp)
        log_message(call_params, pretty=True)

        retn = resp.json()

        return retn

    def by_email(self, email):

        return self._pdl_call(dict(email=email))

    def by_name(self, **kwargs):
        name = kwargs.get("name", False)
        first_name = kwargs.get("first_name", False)
        last_name = kwargs.get("last_name", False)
        company = kwargs.get("company", False)
        phone = kwargs.get("phone", False)

        params = dict()

        if name:
            params.update(name=name)

        if first_name and last_name:
            params.update(dict(name=" ".join([first_name, last_name])))

        if company:
            params.update(dict(company=company))

        if phone:
            params.update(dict(phone=re.sub(r"\D", "", phone)))

        return self._pdl_call(params)

    def by_social_profile(self, profile_address):

        return self._pdl_call(dict(profile=profile_address))



