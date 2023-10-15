ADMIN_CONFIG = {
    "ADMIN_NAME": "Admin",
    "HEADER_DATE_FORMAT": "l, F j Y",
    "HEADER_TIME_FORMAT": "h:i A",
    "SHOW_DJANGO_SIDEBAR": False,
    "MENU": (
        {
            "label": "Users",
            "icon": "fas fa-user",
            "models": [
                "auth.user",
                "auth.group",
                # "simple_otp.UserProfile",
                # "simple_otp.UserToken",
                # "simple_otp.UserOTP",
                # "simple_otp.UserFailedLogin",
            ],
        },
        {"label": "Blog", "icon": "fas fa-people-arrows", "app": "blog"},
        {"label": "Planner", "icon": "fas fa-people-arrows", "app": "planner"},
        {"label": "Weather", "icon": "fas fa-people-arrows", "app": "weather"},
        {"label": "Content", "icon": "fas fa-code", "app": "content"},
        {"label": "Navbar", "icon": "fas fa-code", "app": "navbar"},
        {"label": "API", "icon": "fas fa-database", "app": "api"},
        {"label": "App", "icon": "fas fa-clock", "app": "app"},
        {"label": "GIS", "icon": "fas fa-map-marked", "app": "gis"},
        {"label": "POI", "icon": "fas fa-map-marked", "app": "poi"},
        {"label": "Kids", "icon": "fas fa-map-marked", "app": "kids"},
        {"label": "LiveChat", "icon": "fas fa-map-marked", "app": "livechat"},
        {"label": "Me", "icon": "fas fa-map-marked", "app": "me"},
        {"label": "Hiking", "icon": "fas fa-map-marked", "app": "hiking"},
        {"label": "Admin", "icon": "fas fa-tools", "app": "custom_admin"},
    ),
}
