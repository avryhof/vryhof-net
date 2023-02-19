from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from livechat.helpers import get_chat_session


@login_required
def fullpage_chat(request, *args, **kwargs):
    template_name = "fullpage-chat.html"

    chat_session = get_chat_session(request)
    context = dict(messages=chat_session.get_messages(True))

    return render(request, template_name, context)
