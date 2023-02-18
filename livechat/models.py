import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import (
    Model,
    ForeignKey,
    DO_NOTHING,
    DateTimeField,
    TextField,
    CharField,
    GenericIPAddressField,
    BooleanField,
    ManyToManyField,
)

from gis.models import GISPoint
from livechat.constants import alphanumeric
from livechat.devices.location.device import Geoname
from utilities.utility_functions import is_empty


class ChatBot(Model):
    bot_name = CharField(max_length=50, blank=True, null=True, validators=[alphanumeric])
    active = BooleanField(default=True)
    bot_user = ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True, on_delete=DO_NOTHING)
    sites = ManyToManyField(Site)
    initial_chat_content = TextField(null=True)


class ChatSession(GISPoint):
    first_name = CharField(max_length=30, blank=False, verbose_name="First Name", validators=[alphanumeric])
    last_name = CharField(max_length=30, blank=False, verbose_name="Last Name", validators=[alphanumeric])
    user = ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=DO_NOTHING)
    ip_address = GenericIPAddressField(blank=True, null=True)
    session_id = CharField(max_length=64, blank=True, null=True)
    created = DateTimeField(auto_now_add=True, blank=True, editable=False)
    last_replied = DateTimeField(auto_now_add=True, blank=True, editable=False)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        name_str = [x for x in [self.first_name, self.last_name] if isinstance(x, str)]
        if not is_empty(name_str):
            self.name = " ".join(name_str)
        elif is_empty(name_str) and not is_empty(self.user):
            self.name = self.user.username

        super(ChatSession, self).save(force_insert, force_update, using, update_fields)

    def get_messages(self, include_sent=False):
        if include_sent:
            messages = ChatMessage.objects.filter(session=self).order_by("sent")
        else:
            messages = ChatMessage.objects.filter(session=self, shown=False).order_by("sent")
            message_count = messages.count()
            if message_count > 0:
                self.last_replied = messages[message_count - 1].sent
                self.save()

        return messages

    def delete(self, using=None, keep_parents=False):
        ChatMessage.objects.filter(session_id=self.pk).delete()

        super(ChatSession, self).delete(using, keep_parents)

    @property
    def expired(self):
        session_expiration = datetime.datetime.now() - datetime.timedelta(days=1)

        return self.last_replied < session_expiration

    @property
    def geo(self):
        return Geoname(latitude=self.latitude, longitude=self.longitude)


class ChatMessage(Model):
    session = ForeignKey(ChatSession, blank=False, null=False, on_delete=DO_NOTHING)
    sender = ForeignKey(settings.AUTH_USER_MODEL, default=None, blank=True, null=True, on_delete=DO_NOTHING)
    sent = DateTimeField(auto_now_add=True, blank=True, editable=False)
    shown = BooleanField(default=False)
    message = TextField(null=True)
    source = CharField(max_length=100, blank=True, null=True)

    @property
    def name(self):
        name = self.session.name

        if is_empty(name):
            name = " ".join([x for x in [self.sender.first_name, self.sender.last_name] if isinstance(x, str)])

        if is_empty(name):
            return self.sender.username

        return name


class NLTKReflections(Model):
    active = BooleanField(default=True)
    reflection_phrase = TextField(null=True)
    reflection = TextField(null=True)

    class Meta:
        verbose_name = "Reflection"
        verbose_name_plural = "Reflections"


class NLTKPairs(Model):
    active = BooleanField(default=True)
    question = TextField(null=True)
    answer = TextField(null=True)

    class Meta:
        verbose_name = "Question pattern"
        verbose_name_plural = "Question Patterns"
