import os
import re

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils.text import slugify

from custom_admin.utility_functions import log_message, is_empty


def get_config(value, default=None):
    suit_config = getattr(settings, "CUSTOM_ADMIN_CONFIG", {})

    return suit_config.get(value, default)


def url_join(*args, **kwargs):
    addslash = kwargs.get("addslash", False)

    os_path = os.path.join(*args)
    path_parts = re.split(r"[/\\]", os_path)

    return "/".join(path_parts) + "/" if addslash else ""


def user_has_permissions(user, permissions):
    if is_empty(permissions):
        return True
    else:
        if not isinstance(permissions, (list, tuple)):
            permissions = [permissions]

        if isinstance(permissions, (list, tuple)):
            for permission in permissions:
                if user.has_perm(permission):
                    return True

    return False


def get_model_config(appname, model_name):
    if is_empty(appname) or is_empty(model_name):
        return None
    return apps.get_model(appname, model_name)


def get_admin_base_url():
    admin_base_url = reverse("admin:index")
    if admin_base_url[-1] != "/":
        admin_base_url = admin_base_url + "/"

    return admin_base_url


def get_admin_model_url(value):
    admin_base_url = get_admin_base_url()

    retn = admin_base_url

    if isinstance(value, dict):
        if value.get("models"):
            value = value.get("models")[0]

    if isinstance(value, str):
        value_parts = value.split(".")

        appname = value_parts[0]
        model_name = None

        if len(value_parts) == 2:
            model_name = value_parts[1]

        if model_name:
            retn = admin_reverse(appname, model_name)

        else:
            retn = os.path.join(admin_base_url, appname)

    return retn


def admin_reverse(appname, model_name):
    admin_base_url = get_admin_base_url()
    base_url_parts = [x for x in admin_base_url.split("/") if not is_empty(x)]
    url_parts = [x.replace("/", "").lower() for x in base_url_parts + [appname, model_name]]
    reversed_url = "/{}/".format("/".join(url_parts))
    if reversed_url[0] != "/":
        reversed_url = "/" + reversed_url
    return reversed_url


def admin_change_link(appname, model_name=None, item_pk=None):
    if isinstance(item_pk, object) and hasattr(item_pk, "pk"):
        item_pk = item_pk.pk

    admin_base_url = get_admin_base_url()

    url_parts = admin_base_url.split("/")
    url_parts.append(appname.replace("/", "").lower())
    url_parts.append(model_name.replace("/", "").lower())
    url_parts.append(str(item_pk))
    url_parts.append("change")

    return "/{}/".format("/".join([x for x in url_parts if not is_empty(x)]))


def menu_url(value):
    if "/" not in value:
        try:
            menu_item_url = reverse(value)
        except NoReverseMatch:
            menu_item_url = get_admin_model_url(value)
    else:
        menu_item_url = value

    return menu_item_url


def menu_icon(value):
    if not is_empty(value):
        if value.startswith("icon-"):
            icon_class = value.replace("icon", "fa fa")
        else:
            icon_class = value
        icon = '<i class="{}"></i>'.format(icon_class)
    else:
        icon = '<i class="admin-menu-icon"></i>'

    return icon


def get_app_models(appname):
    app_models = []
    for url in admin.site.get_urls():
        urlstring = str(url.pattern)

        if appname in urlstring:
            pattern_parts = re.split(r"[/\\]", urlstring)
            app_name = pattern_parts[0]

            if app_name == appname:
                model_name = pattern_parts[1]

                model_config = get_model_config(appname, model_name)
                admin_url = admin_reverse(app_name, model_name)

                app_models.append(
                    {
                        "icon": "fas fa-chevron-right",
                        "import": ".".join([appname, model_name]),
                        "label": str(model_config._meta.verbose_name_plural).title(),
                        "url": admin_url,
                    }
                )

    return app_models


def model_menu_item(model):
    label = ""
    permissions = ()

    if isinstance(model, dict):
        label = model.get("label")
        permissions = model.get("permissions")
        model = model.get("model_name")

    if not is_empty(model) and isinstance(model, str):
        try:
            appname, modelname = model.split(".")
        except ValueError:
            log_message("{} -> {}".format(label, model))
        else:
            try:
                model_config = apps.get_model(appname, modelname)
            except LookupError:
                return None

            if is_empty(label):
                label = str(model_config._meta.verbose_name_plural)

    return {"label": label.title(), "permissions": permissions, "model_name": str(model)}


def render_menu_item(menu_item, request, level=1):
    """
    Determine if a menu item should be rendered for the logged-in user, and return the following if it should.
    - Label
    - Icon
    - URL
    """
    user = request.user

    item_lines = []

    if isinstance(menu_item, dict):
        admin_base_url = get_admin_base_url()

        label = ""
        icon = '<i class="fas fa-chevron-circle-right"></i>'
        url = admin_base_url

        classnames = ["sidebar-item"]

        if user_has_permissions(user, menu_item.get("permissions")):
            classnames.append("level-{}".format(level))

            # Process the label
            label = menu_item.get("label")
            if is_empty(label) and "model_name" in menu_item:
                model_appname = menu_item.get("app")
                model_model_name = menu_item.get("model_name")

                if is_empty(model_appname) and "." in model_model_name:
                    model_appname = model_model_name.split(".")[0]
                    model_model_name = model_model_name.split(".")[1]

                model_config = get_model_config(model_appname, model_model_name)

                if not is_empty(model_config):
                    label = str(model_config._meta.verbose_name_plural).title()
                else:
                    label = menu_item.get("model_name")

            if is_empty(label) and "app" in menu_item:
                label = " ".join(menu_item.get("app").split("_")).title()

            if "icon" in menu_item:
                icon = menu_icon(menu_item.get("icon"))

            if "models" in menu_item or "app" in menu_item:
                classnames.append("parent")
                label_slug = slugify(label)

                submenu_lines = []

                models = menu_item.get("models")

                if not is_empty(models):
                    for model in models:
                        if not isinstance(model, dict):
                            submenu_lines.append(render_menu_item(model_menu_item(model), request, (level + 1)))

                        else:
                            submenu_lines.append(render_menu_item(model, request, (level + 1)))

                if "app" in menu_item and is_empty(models):
                    app_models = get_app_models(menu_item.get("app"))
                    submenu_lines = [render_menu_item(x, request, (level + 1)) for x in app_models]

                item_lines = [
                    '<div class="{}">'.format(" ".join(classnames)),
                    '<input type="checkbox" class="submenu-control" name="{}" id="{}">'.format(label_slug, label_slug),
                    '<label for="{}">'.format(label_slug),
                    '<div class="icon">{}</div>'.format(icon),
                    '<div class="sidebar-label">{}</div>'.format(label),
                    "</label>",
                    '<div class="submenu">',
                    "".join(submenu_lines),
                    "</div>",
                    "</div>",
                ]

            else:
                if "url" in menu_item:
                    url = menu_url(menu_item.get("url"))

                elif "model_name" in menu_item:
                    url = menu_url(menu_item.get("model_name"))

                absolute_url = request.build_absolute_uri()
                url_contain_string = url.replace("/proact-admin/", "")

                is_home = is_empty(url_contain_string) and absolute_url.endswith(reverse("admin:index"))
                is_active = not is_empty(url_contain_string) and url_contain_string in absolute_url

                if is_home or is_active:
                    classnames.append("active")

                item_lines = [
                    '<div class="{}">'.format(" ".join(classnames)),
                    '<a href="{}">'.format(url) if not is_empty(url) else '<a name="{}">'.format(label),
                    '<div class="icon">{}</div>'.format(icon),
                    '<div class="sidebar-label">{}</div>'.format(label),
                    "</a>",
                    "</div>",
                ]

    return "".join([item_line for item_line in item_lines if isinstance(item_line, str)])
