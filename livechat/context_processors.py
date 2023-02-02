from livechat.helpers import get_chat_bot


def livechat_context(request):
    chat_bot = get_chat_bot(request)

    return dict(chat_bot=chat_bot)
