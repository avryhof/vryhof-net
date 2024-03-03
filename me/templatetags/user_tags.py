from django import template
from django.utils.safestring import mark_safe

from accounts.utils import not_empty
from me.helpers import get_profile
from utilities.model_helper import load_model

register = template.Library()


@register.simple_tag()
def user_icon(request):
    icon_html = '<div class="user-icon">'

    if request.user.is_authenticated:
        profile = get_profile(request)
        if not_empty(profile) and isinstance(profile.first_name, str):
            icon_html += f'<div class="user-initial">{profile.first_name[0].upper()}</div>'
        else:
            icon_html += f'<div class="user-initial">{request.user.username[0].upper()}</div>'
    else:
        icon_html += '<img src="/static/icons/feather/user.svg" alt="User">'

    icon_html += "</div>"

    return mark_safe(icon_html)


@register.simple_tag()
def user_name(request):
    if request.user.is_authenticated:
        profile = get_profile(request)
        if not_empty(profile) and not_empty(profile.name):
            return profile.name
    return request.user.username
