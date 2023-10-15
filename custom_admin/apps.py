# -*- coding: utf-8 -*-
from django import get_version
from django.apps import AppConfig


class CustomAdminConfig(AppConfig):
    name = "custom_admin"
    verbose_name = "Custom Admin"
    django_version = get_version()
    version = "0.1"

    def __init__(self, app_name, app_module):
        super(CustomAdminConfig, self).__init__(app_name, app_module)

    def ready(self):
        super(CustomAdminConfig, self).ready()


