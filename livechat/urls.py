from django.urls import path

from livechat.api_views import add_message, start_chat, get_session_messages

urlpatterns = [
    path("start-chat/", start_chat, name="start-chat"),
    path("send-message/", add_message, name="send-message"),
    path("get-messages/", get_session_messages, name="get-messages"),
]
