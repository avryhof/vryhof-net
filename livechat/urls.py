from django.urls import path

from livechat.views import fullpage_chat

urlpatterns = [
    path("", fullpage_chat, name="full-chat"),
]
