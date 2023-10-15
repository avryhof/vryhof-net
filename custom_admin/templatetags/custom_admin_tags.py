from django import template, __version__
from django.utils.safestring import mark_safe

from custom_admin.utility_functions import aware_now, is_empty, php_date, make_list
from custom_admin.utils import get_admin_model_url, get_config, render_menu_item

register = template.Library()


@register.simple_tag
def django_version():
    retn = float(__version__)

    return retn


@register.simple_tag
def new_django():
    version = float(__version__) > 4.0
    retn = version > 4

    return retn


@register.simple_tag
def admin_config(config_var):
    return get_config(config_var)


@register.simple_tag
def active_breadcrumb(title):
    html = '<li class="active">%s</li>' % title

    return mark_safe(html)


@register.simple_tag
def breadcrumb(title, link):
    html = '<li><a href="%s">%s</a><span class="divider">»</span></li>' % (link, title)

    return mark_safe(html)


@register.simple_tag
def custom_title(default=None):
    site_title = default
    config_title = get_config("ADMIN_NAME", site_title)

    if not is_empty(config_title):
        site_title = config_title

    return get_config("ADMIN_NAME", site_title)


@register.simple_tag
def custom_time():
    now = aware_now()

    date_format = get_config("HEADER_DATE_FORMAT", "%A, %B %d, %Y")
    time_format = get_config("HEADER_TIME_FORMAT", "%I:%M %p")

    if "%" in date_format:
        formatted_date = now.strftime(date_format)
    else:
        formatted_date = php_date(now, date_format)

    if "%" in time_format:
        formatted_time = now.strftime(time_format)
    else:
        formatted_time = php_date(now, time_format)

    html = (
        '<div class="custom-time">'
        '<div class="custom-time-icon"><i class="far fa-clock"></i></div>'
        '<div class="custom-time-display">'
        '<div class="custom-date">{}</div>'
        '<div class="custom-timestamp">{}</div>'
        "</div>"
        "</div>".format(formatted_date, formatted_time)
    )

    return mark_safe(html)


@register.simple_tag
def custom_url(value):
    return get_admin_model_url(value)


@register.simple_tag
def quick_filter(filter_element=False):
    html = ""
    if filter_element:
        html = '<input type="text" class="filter-field" data-element="%s" autocomplete="off">' % filter_element

    return mark_safe(html)


@register.simple_tag
def get_custom_menu(request):
    """
    The whole idea of this is to replace Django Suit, so we aren't relying on a non-standard admin template
    but we DO want the sidebar so our previous documentation doesn't break.
    :return:
    """
    menu_lines = [render_menu_item({"label": "Home", "icon": "fas fa-home", "url": "admin:index"}, request)]

    menu_items = get_config("MENU")
    for menu_item in menu_items:
        menu_lines.append(render_menu_item(menu_item, request))

    menu_html = "".join(menu_lines)

    return mark_safe(menu_html)


@register.simple_tag
def prepend_custom_menu(request):
    return ""
