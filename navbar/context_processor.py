from navbar.models import NavbarMenu


def menu_item(nav):
    retn = {}

    if not nav.submenu:
        retn = {"title": nav.title, "link": nav.link, "target": nav.target}
    else:
        retn = []
        for subnav in nav.submenu:
            retn.append(menu_item(subnav))

    return retn


def navmenu_context(request):
    return_dict = {}

    try:
        navmenu = NavbarMenu.objects.get(root_menu=True)
    except NavbarMenu.DoesNotExist:
        pass
    else:
        menu = []

        for nav in navmenu.menu_items.iterator():
            menu.append(menu_item(nav))

        return_dict["navmenu"] = menu

    return return_dict
