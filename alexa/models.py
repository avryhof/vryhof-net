from django.db import models
from django_extensions.db.fields.json import JSONField

from alexa.alexa_functions import rebuild_interaction_model


class Intent(models.Model):
    enabled = models.BooleanField(default=True)
    name = models.CharField(max_length=255, null=True)
    samples = JSONField(null=True)

    def __str__(self):
        return self.name


class LanguageModel(models.Model):
    enabled = models.BooleanField(default=True)
    invocation_name = models.CharField(max_length=255, blank=True, null=True)
    intents = models.ManyToManyField(Intent, blank=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(LanguageModel, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

        rebuild_interaction_model(self)


class BedtimeStory(models.Model):
    enabled = models.BooleanField(default=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    story = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Bedtime Story'
        verbose_name_plural = 'Bedtime Stories'

    def __str__(self):

        return self.title
