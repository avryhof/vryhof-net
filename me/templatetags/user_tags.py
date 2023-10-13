from django import template
from django.utils.safestring import mark_safe

from utilities.utility_functions import is_empty

register = template.Library()


@register.simple_tag()
def user_icon(request):
    icon_html = '<div class="user-icon">'

    if request.user.is_authenticated and not is_empty(request.user.email):
        icon_html += request.user.username[0].upper()
    else:
        icon_html += '<i class="fa-solid fa-user"></i>'

    icon_html += "</div>"

    return mark_safe(icon_html)


@register.simple_tag()
def user_name(request):
    return request.user.username
