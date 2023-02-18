import datetime

import bleach
import openai
from django.conf import settings
from nltk.chat.util import Chat
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from livechat.constants import API_RESULT_KEY, NO_CACHE_HEADERS, API_GENERIC_FAILURE, API_GENERIC_SUCCESS
from livechat.forms import ChatMessageForm
from livechat.helpers import get_chat_session, get_pairs, get_reflections, get_chat_bot
from livechat.models import ChatMessage
from livechat.personal_assistant.classes import Bot
from utilities.debugging import log_message
from utilities.utility_functions import is_empty, aware_now, get_client_ip

openai.api_key = getattr(settings, "OPENAI_API_KEY")


@api_view(["GET"])
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
def add_message(request):
    chat_session = get_chat_session(request)
    chat_bot = get_chat_bot(request)

    message = bleach.clean(request.data.get("message"))

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
                    message=message.strip(),
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
                response_source = "NLTK Refelections"

                if is_empty(chat_response):
                    bot = Bot(chat_session=chat_session, client_ip=get_client_ip(request), debug=False)
                    chat_response, response_source = bot.respond(chat_query)

                if not is_empty(chat_response):
                    ChatMessage.objects.create(
                        session=chat_session,
                        sender=chat_user,
                        sent=response_time,
                        message=chat_response.strip(),
                        source=response_source
                    )

    return Response({API_RESULT_KEY: result}, status=response_status, headers=NO_CACHE_HEADERS)


@api_view(["POST"])
def set_location(request):
    chat_session = get_chat_session(request)

    chat_session.latitude = request.data.get("latitude")
    chat_session.longitude = request.data.get("longitude")
    chat_session.save()

    result = API_GENERIC_SUCCESS
    response_status = status.HTTP_200_OK

    return Response({API_RESULT_KEY: result}, status=response_status, headers=NO_CACHE_HEADERS)
