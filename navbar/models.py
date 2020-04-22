# -*- coding: utf-8 -*-
from django.db.models import (
    Model,
    URLField,
    CharField,
    BooleanField,
    IntegerField,
    ManyToManyField,
    ForeignKey,
    DO_NOTHING,
)


class NavbarLink(Model):
    LINK_TARGET_SELF = "_self"
    LINK_TARGET_BLANK = "_blank"
    LINK_TARGET_TOP = "_top"
    LINK_TARGET_CHOICES = (
        (LINK_TARGET_SELF, "Normal"),
        (LINK_TARGET_TOP, "Break Frames"),
        (LINK_TARGET_BLANK, "New Tab/Window"),
    )

    active = BooleanField(default=True)
    order = IntegerField()
    title = CharField(max_length=128, blank=True, null=True)
    link = URLField(blank=True, null=True)
    target = CharField(max_length=16, choices=LINK_TARGET_CHOICES, default=LINK_TARGET_SELF)
    submenu = ForeignKey("NavbarMenu", blank=True, null=True, on_delete=DO_NOTHING)

    def __str__(self):
        retn = "NavbarLink %i" % self.pk

        if self.submenu:
            retn = self.submenu

        elif self.title:
            retn = self.title

        return retn


class NavbarMenu(Model):
    active = BooleanField(default=True)
    root_menu = BooleanField(default=False)
    order = IntegerField()
    name = CharField(max_length=128, blank=True, null=True)
    menu_items = ManyToManyField(NavbarLink, blank=True)

    def __str__(self):
        retn = "NavbarMenu %i" % self.pk

        if self.name:
            retn = self.name

        return retn
