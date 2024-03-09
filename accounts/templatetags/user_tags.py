from django import template

register = template.Library()


@register.simple_tag
def user_name(request):
    return request.user.username


@register.simple_tag
def user_icon(request):
    return ""
