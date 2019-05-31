# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import MailMessage


@admin.register(MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'received', 'message')
    list_filter = ('received',)