"""
@copyright Copyright KPH Healthcare Services, Inc., 2017

Insert description here
"""
from __future__ import unicode_literals
from django.conf import settings
from rest_framework import permissions

from assistant.models import AuthorizedAgent


class AuthorizedAgentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        is_authorized = False

        try:
            AuthorizedAgent.objects.get(authorized=True, app_key=request.auth)

        except AuthorizedAgent.DoesNotExist:
            pass

        else:
            is_authorized = True

        return is_authorized
