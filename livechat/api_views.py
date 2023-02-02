import datetime

import bleach
import openai
from django.conf import settings
from nltk.chat.util import Chat
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.rest_auth import CsrfExemptSessionAuthentication
from livechat.constants import API_RESULT_KEY, NO_CACHE_HEADERS, API_GENERIC_FAILURE, API_GENERIC_SUCCESS
from livechat.forms import ChatMessageForm
from livechat.helpers import get_chat_session, get_pairs, get_reflections, parse_response_template, get_chat_bot
from livechat.models import ChatMessage
from utilities.debugging import log_message
from utilities.utility_functions import is_empty, aware_now

openai.api_key = getattr(settings, "OPENAI_API_KEY")


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((CsrfExemptSessionAuthentication,))
def get_session_messages(request, **kwargs):
    messages = []

    continue_chat = request.GET.get("continue_chat") == "true"

    chat_session = get_chat_session(request)
    new_messages = chat_session.get_messages(include_sent=continue_chat)

    if new_messages.count() > 0:
        chat_bot = get_chat_bot(request)

        for message in new_messages:
            message.shown = True
            message.save()

            if not is_empty(message.sender):
                msg_name = None
                message_type = None

                if message.sender == chat_bot.bot_user:
                    msg_name = chat_bot.bot_name
                    message_type = "received"

                elif message.sender == request.user:
                    msg_name = message.name
                    message_type = "sent"

                messages.append(
                    {
                        "name": msg_name,
                        "message": message.message,
                        "sent": message.sent.isoformat(),
                        "type": message_type,
                    }
                )

    return Response({API_RESULT_KEY: messages}, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((CsrfExemptSessionAuthentication,))
def start_chat(request):
    chat_session = get_chat_session(request)

    first_name = bleach.clean(request.POST.get("first_name"))
    last_name = bleach.clean(request.POST.get("last_name"))
    date_of_birth = bleach.clean(request.POST.get("date_of_birth"))

    if request.user.is_authenticated:
        first_name = request.user.first_name if request.user.first_name else first_name
        last_name = request.user.last_name if request.user.last_name else last_name

    result = API_GENERIC_FAILURE
    response_status = status.HTTP_401_UNAUTHORIZED

    if first_name and last_name and date_of_birth:
        chat_session.first_name = first_name
        chat_session.last_name = last_name
        chat_session.date_of_birth = date_of_birth
        chat_session.save()

        result = API_GENERIC_SUCCESS
        response_status = status.HTTP_200_OK

    return Response({API_RESULT_KEY: result}, status=response_status, headers=NO_CACHE_HEADERS)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((CsrfExemptSessionAuthentication,))
def add_message(request):
    chat_session = get_chat_session(request)
    chat_bot = get_chat_bot(request)

    message = bleach.clean(request.POST.get("message"))

    form = ChatMessageForm(request.POST)

    result = API_GENERIC_FAILURE
    response_status = status.HTTP_401_UNAUTHORIZED

    if not form.is_valid():
        log_message(form)

    else:
        if request.user.is_authenticated:
            sent_time = aware_now()
            try:
                ChatMessage.objects.create(
                    session=chat_session,
                    sender=request.user,
                    sent=sent_time,
                    message=message,
                    source="Authenticated User",
                )

            except Exception as e:
                log_message("Failed to create object: %s" % e)

            else:
                result = API_GENERIC_SUCCESS
                response_status = status.HTTP_200_OK

                chat_user = chat_bot.bot_user
                response_time = sent_time + datetime.timedelta(seconds=1)

                pairs = get_pairs()
                reflections = get_reflections()

                chat = Chat(pairs, reflections)
                chat_query = message.lower()
                chat_response = chat.respond(chat_query)

                if is_empty(chat_response):
                    try:
                        completions = openai.Completion.create(
                            engine="text-davinci-002",
                            prompt=message,
                            max_tokens=1024,
                            n=1,
                            stop=None,
                            temperature=0.5,
                        )

                    except Exception as e:
                        chat_response = f"I can't answer that, {chat_session.name}."
                        chat_source = "Error message"

                    else:
                        chat_response = completions.choices[0].text
                        chat_source = "OpenAI"

                else:
                    chat_response = parse_response_template(chat_response)
                    chat_source = "NLTK Responder"

                if not is_empty(chat_response):
                    ChatMessage.objects.create(
                        session=chat_session,
                        sender=chat_user,
                        sent=response_time,
                        message=chat_response,
                        source=chat_source,
                    )

    return Response({API_RESULT_KEY: result}, status=response_status, headers=NO_CACHE_HEADERS)
