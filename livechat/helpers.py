import base64
import datetime
import os
import re

from django.conf import settings
from django.urls import reverse
from django.utils.timezone import make_aware
from nltk.chat.util import reflections

from livechat.constants import API_FORWARD_IP_KEY
from livechat.models import ChatSession, NLTKPairs, NLTKReflections
from utilities.debugging import log_message


def check_forwarded_ip(user_ip, request):
    """When requests come from the website we get the IP of the server rather than the IP of the user when we hit
    the api level.  To fix this, when a request can be verified to come from the webserver then look for a
    forwarded ip of the user and if it is present use that for user ip.

    :param user_ip Real IP as gotten from HTTP request
    :param request the django rest framework request
    :return IP to use, either original (None if not provided) or a forwarded IP if request from this server and sent
    """

    if user_ip:
        # Make sure we use forwarded user ip when request comes from website only
        server_ip = getattr(settings, "SERVER_IP", "")

        if user_ip == server_ip:
            website_requestor = getattr(settings, "WEBSITE_KPH_AGENT", "")

            if request.auth == website_requestor:
                forwarded_ip = request.data.get(API_FORWARD_IP_KEY, None)

                if forwarded_ip:
                    user_ip = forwarded_ip

    return user_ip


def bytes_to_str(value):
    if isinstance(value, str) and value[0:2] == "b'":
        value = value[2:-1]

    return value


def generate_token():
    raw_token = os.urandom(32)
    base64_token = str(base64.b64encode(raw_token))
    encoded_token = bytes_to_str(base64_token)

    return encoded_token


def get_chat_session(request):
    session_expiration = make_aware(datetime.datetime.now()) - datetime.timedelta(days=1)

    session_id = request.session.get("chat_id")
    if not session_id:
        session_id = generate_token()
        request.session["chat_id"] = session_id

    try:
        chat_session = ChatSession.objects.get(user=request.user, last_replied__gt=session_expiration)
    except ChatSession.DoesNotExist:
        chat_session = ChatSession.objects.create(
            user=request.user, last_replied=make_aware(datetime.datetime.now())
        )

    return chat_session


def get_reflections():
    return_reflections = reflections

    for my_reflection in NLTKReflections.objects.filter(active=True):
        return_reflections.update({my_reflection.reflection_phrase: my_reflection.reflection})

    return return_reflections


def get_pairs():
    pairs = []

    nltk_pairs = NLTKPairs.objects.filter(active=True)

    for pair in nltk_pairs:
        pairs.append([pair.question, [pair.answer]])

    return pairs


def response_template_function(function_name, function_parameter):
    return_value = ""

    if function_name == "url":
        return_value = reverse(function_parameter)

    elif function_name == "answer":
        return_value = '<a href="#" class="chat-answer">%s</a>' % function_parameter

    return return_value


def parse_response_template(response):
    return_value = response

    if "{" in response and "}" in response:
        tags = re.findall(r"\{ (.+?) \}", response)

        for tag in tags:
            tag = tag.strip()
            if "(" in tag:
                tag_function = re.match(r"([A-Za-z0-9_]+)\('(.+?)'\)", tag)
                tag_replace = "{ %s }" % tag
                tag_value = response_template_function(*tag_function.groups())
                return_value = return_value.replace(tag_replace, tag_value)

    return return_value
