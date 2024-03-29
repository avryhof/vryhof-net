# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import ChatSession, ChatMessage, ChatBot


@admin.register(ChatBot)
class ChatBotAdmin(admin.ModelAdmin):
    list_display = (
        "bot_name",
        "active",
    )
    filter_horizontal = ("sites",)


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "user",
        "ip_address",
        "session_id",
        "created",
        "last_replied",
    )
    list_display_links = (
        "first_name",
        "last_name",
        "session_id",
    )
    list_filter = ("user", "created", "last_replied")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "sender", "sent", "shown", "message")
    list_filter = ("session", "sender", "sent", "shown")
