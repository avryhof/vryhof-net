from django.urls import path

from livechat.api_views import add_message, get_session_messages, set_location

urlpatterns = [
    path("send-message/", add_message, name="send-message"),
    path("get-messages/", get_session_messages, name="get-messages"),
    path("set-location/", set_location, name="set-chat-location"),
]
