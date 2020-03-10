import datetime

import bleach
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from nltk.chat.util import Chat
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.rest_auth import CsrfExemptSessionAuthentication
from livechat.constants import API_RESULT_KEY, NO_CACHE_HEADERS, API_GENERIC_FAILURE, API_GENERIC_SUCCESS
from livechat.forms import ChatMessageForm
from livechat.helpers import get_chat_session, get_pairs, get_reflections, parse_response_template
from livechat.models import ChatMessage
from utilities.debugging import log_message


@api_view(["GET"])
@permission_classes((AllowAny,))
@authentication_classes((CsrfExemptSessionAuthentication,))
def get_session_messages(request, **kwargs):
    messages = []

    continue_chat = request.GET.get("continue_chat") == "true"

    chat_session = get_chat_session(request)
    new_messages = chat_session.get_messages(include_sent=continue_chat)

    if new_messages.count() > 0:
        for message in new_messages:
            message.shown = True
            message.save()

            msg_name = "%s %s" % (chat_session.first_name, chat_session.last_name)

            if message.sender:
                msg_name = "%s %s" % (message.sender.first_name, message.sender.last_name)

            elif request.user.is_authenticated:
                msg_name = "%s %s" % (request.user.first_name, request.user.last_name)

            if message.sender == request.user:
                message_type = "sent"
            else:
                message_type = "received"

            messages.append(
                {"name": msg_name, "message": message.message, "sent": message.sent.isoformat(), "type": message_type}
            )

    return Response({API_RESULT_KEY: messages}, status=status.HTTP_200_OK, headers=NO_CACHE_HEADERS,)


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

    return Response({API_RESULT_KEY: result,}, status=response_status, headers=NO_CACHE_HEADERS,)


@api_view(["POST"])
@permission_classes((AllowAny,))
@authentication_classes((CsrfExemptSessionAuthentication,))
def add_message(request):
    chat_session = get_chat_session(request)

    message = bleach.clean(request.POST.get("message"))

    form = ChatMessageForm(request.POST)

    result = API_GENERIC_FAILURE
    response_status = status.HTTP_401_UNAUTHORIZED

    if form.is_valid():
        sent_time = make_aware(datetime.datetime.now())
        try:
            if request.user.is_authenticated:
                ChatMessage.objects.create(session=chat_session, sender=request.user, sent=sent_time, message=message)
            else:
                ChatMessage.objects.create(session=chat_session, sent=sent_time, message=message)

        except Exception as e:
            print("Failed to create object: %s" % e)

        else:
            result = API_GENERIC_SUCCESS
            response_status = status.HTTP_200_OK

            auth_user = get_user_model()
            try:
                chat_user = auth_user.objects.get(username="chatbot")
            except auth_user.DoesNotExist:
                ChatMessage.objects.create(session=chat_session, sent=sent_time, message="Chat Bot offline!")
            else:
                response_time = sent_time + datetime.timedelta(seconds=1)

                pairs = get_pairs()
                reflections = get_reflections()

                chat = Chat(pairs, reflections)
                chat_query = message.lower()
                chat_response = chat.respond(chat_query)
                if chat_response is None:
                    first_name = request.user.first_name if request.user.first_name else "Dave"
                    chat_response = "I can't answer that, %s." % first_name
                else:
                    chat_response = parse_response_template(chat_response)
                ChatMessage.objects.create(
                    session=chat_session, sender=chat_user, sent=response_time, message=chat_response
                )

    return Response({API_RESULT_KEY: result,}, status=response_status, headers=NO_CACHE_HEADERS,)
