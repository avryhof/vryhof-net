from django.db import models
from django_extensions.db.fields.json import JSONField


class MailMessage(models.Model):
    received = models.DateTimeField(auto_now_add=True, null=True)
    message = JSONField(null=True)
