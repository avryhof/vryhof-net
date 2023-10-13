from django import template
from django.utils.safestring import mark_safe

from content.models import SidebarItem
from utilities.model_helper import load_model
from utilities.utility_functions import is_empty

register = template.Library()


@register.simple_tag
def page_content(page):
    blocks = []

    if not is_empty(page):
        for block in page.content_blocks:
            blocks.append(f'<div class="content-block">{block.content}</div>')

    return mark_safe("".join(blocks))


@register.simple_tag
def sidebar_icon(url_name, icon_class):
    page_model = load_model("frontend.Page")

    try:
        page = page_model.objects.get(url_name=url_name)
    except page_model.DoesNotExist:
        return ""
    else:
        return mark_safe(
            '<div class="sidebar-item">'
            f'<a href="{page.page_url}">'
            f'<div class="icon"><i class="{icon_class} fa-2x"></i></div>'
            f'<div class="label">{page.page_title}</div>'
            "</a></div>"
        )


@register.simple_tag
def sidebar_items(authenticated=False):
    return mark_safe("".join([item.html for item in SidebarItem.objects.filter(authenticated=authenticated).order_by("order")]))