from django.db.models import TextField
from django.forms import Form


class ChatMessageForm(Form):
    message = TextField(blank=False)

