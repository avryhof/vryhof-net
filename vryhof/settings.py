"""
Django settings for vryhof project.

Generated by 'django-admin startproject' using Django 1.11.17.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""
import os

from vryhof.admin_settings import ADMIN_CONFIG

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.join(os.environ['VRYHOF_HOME'], 'htdocs')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["VRYHOF_SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

CUSTOM_ADMIN_CONFIG = ADMIN_CONFIG

SITE_PROTO = "http"

ALLOWED_HOSTS = []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Application definition
INSTALLED_APPS = [
    "daphne",
    "custom_admin",
    "django.contrib.admin",
    "django.contrib.postgres",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "channels",
    "accounts",
    "me",
    "bootstrap4",
    "rest_framework",
    "django_extensions",
    "easy_thumbnails",
    "filer",
    "ckeditor",
    "ckeditor_filebrowser_filer",
    "ckeditor_uploader",
    "mptt",
    "favorites_icons",
    "gis",
    "content",
    "navbar",
    "firefox",
    "livechat",
    "weather",
    "blog",
    "planner",
    "utilities",
    "poi",
    "api",
    "kids",
    "app",
    "subsonic",
    "amos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "vryhof.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "custom_admin", "templates"),
            os.path.join(BASE_DIR, "firefox", "templates"),
            os.path.join(BASE_DIR, "blog", "templates"),
            os.path.join(BASE_DIR, "livechat", "templates"),
            os.path.join(BASE_DIR, "weather", "templates"),
            os.path.join(BASE_DIR, "poi", "templates"),
            os.path.join(BASE_DIR, "kids", "templates"),
            os.path.join(BASE_DIR, "me", "templates"),
            os.path.join(BASE_DIR, "amos", "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "navbar.context_processor.navmenu_context",
                "utilities.context_processors.website_context",
                "livechat.context_processors.livechat_context",
            ]
        },
    }
]

WSGI_APPLICATION = "vryhof.wsgi.application"
ASGI_APPLICATION = "vryhof.asgi.application"

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.environ["VRYHOF_DB_ENGINE"],
        "NAME": os.environ["VRYHOF_DB_NAME"],
        "USER": os.environ["VRYHOF_DB_USER"],
        "PASSWORD": os.environ["VRYHOF_DB_PASSWORD"],
        "HOST": os.environ["VRYHOF_DB_HOST"],
        "PORT": os.environ["VRYHOF_DB_PORT"],
        "CONN_MAX_AGE": 600,
    }
}

AUTHENTICATION_BACKENDS = (
    "accounts.backends.MSGraphBackend",
    "django.contrib.auth.backends.ModelBackend",
)

MS_TENANT_ID = os.environ.get("MS_TENANT_ID")
MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")

MS_SECURE_TRANSPORT = False
MS_RELAX_TOKEN_SCOPE = True
MS_IGNORE_SCOPE_CHANGE = True

ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_REDIRECT_URL = "firefox_home"
ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USER_DISPLAY =
SIGNUP_ENABLED = False

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

MULTIFACTOR = {
    "LOGIN_CALLBACK": False,  # False, or dotted import path to function to process after successful authentication
    "RECHECK": True,  # Invalidate previous authorisations at random intervals
    "RECHECK_MIN": 60 * 60 * 3,  # No recheks before 3 hours
    "RECHECK_MAX": 60 * 60 * 6,  # But within 6 hours
    "FIDO_SERVER_ID": "example.com",  # Server ID for FIDO request
    "FIDO_SERVER_NAME": "Django App",  # Human-readable name for FIDO request
    "TOKEN_ISSUER_NAME": "Django App",  # TOTP token issuing name (to be shown in authenticator)
    "U2F_APPID": "https://localhost",  # U2F request issuer
    "FACTORS": ["FIDO2", "U2F", "TOTP"],  # <- this is the default
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/New_York"

USE_I18N = True

USE_L10N = True

USE_TZ = True

X_FRAME_OPTIONS = "SAMEORIGIN"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

GEOIP_KEY = os.environ.get("GEOIP_KEY")
NWS_EMAIL = "amos@vryhof.net"

BASE_RESPONDER = "chatgpt"
SKILLS_REGISTRY = []

LOCATION = None

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "custom_admin", "static"),
    os.path.join(BASE_DIR, "firefox", "static"),
    os.path.join(BASE_DIR, "livechat", "static"),
    os.path.join(BASE_DIR, "blog", "static"),
    os.path.join(BASE_DIR, "poi", "static"),
    os.path.join(BASE_DIR, "weather", "static"),
    os.path.join(BASE_DIR, "kids", "static"),
    os.path.join(BASE_DIR, "me", "static"),
    os.path.join(BASE_DIR, "amos", "static"),
)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")

CKEDITOR_BASEPATH = "%s%s" % (STATIC_URL, "ckeditor/ckeditor/")
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_BROWSE_SHOW_DIRS = True
# CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "Custom",
        "toolbar_Custom": [
            {"name": "document", "items": ["Print", "Preview"]},
            {"name": "spelling", "items": ["Scayt"]},
            {
                "name": "clipboard",
                "items": [
                    "Cut",
                    "Copy",
                    "Paste",
                    "PasteText",
                    "PasteFromWord",
                    "RemoveFormat",
                ],
            },
            {"name": "history", "items": ["Undo", "Redo"]},
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            {
                "name": "insert",
                "items": [
                    "FilerImage",
                    # "Image",
                    "Table",
                    "HorizontalRule",
                    "SpecialChar"],
            },
            {
                "name": "editing",
                "items": ["Find", "Replace", "-", "SelectAll", "ShowBlocks"],
            },
            {"name": "embedding", "items": ["Iframe"]},
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "basicstyles", "items": ["Bold", "Italic", "Underline"]},
            {
                "name": "paragraph",
                "items": [
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                    "-",
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "TextColor",
                ],
            },
            {"name": "code", "items": ["Maximize", "Source"]},
        ],
        "tabSpaces": 4,
        "extraPlugins": ",".join(
            [
                "uploadimage",  # the upload image feature
                "filerimage",
                # your extra plugins here
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                # "devtools",
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
                "uploadimage",
                "codesnippet",
                "stylesheetparser",
            ]
        ),
    }
}

# ERROR_LOG = os.path.join(os.path.dirname(BASE_DIR), "logs", "error.log")
#
# try:
#     LOGGER_LEVEL = os.environ["LOGGER_LEVEL"]
# except KeyError:
#     LOGGER_LEVEL = "ERROR"
#
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "detailed": {
#             "format": "%(asctime)s %(levelname)s [%(name)s: %(pathname)s %(funcName)s line:%(lineno)s] -- %(message)s",
#             "datefmt": "%m-%d-%Y %H:%M:%S",
#         },
#         "verbose": {
#             "format": "%(asctime)s %(levelname)s %(name)s -- %(message)s",
#             "datefmt": "%m-%d-%Y %H:%M:%S",
#         },
#         "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
#     },
#     "handlers": {
#         "weather": {
#             "level": "INFO",
#             "class": "logging.handlers.RotatingFileHandler",
#             "formatter": "verbose",
#             "filename": os.path.join(os.path.dirname(BASE_DIR), "logs", "weather.log"),
#             "maxBytes": 1024 * 1024 * 100,  # 100 mb
#             "backupCount": 3,
#         },
#         "file": {
#             "level": LOGGER_LEVEL,
#             "class": "logging.FileHandler",
#             "filename": ERROR_LOG,
#         },
#     },
#     "loggers": {
#         "": {"level": "INFO", "handlers": ["weather"], "propagate": True},
#         "django": {"handlers": ["file"], "level": LOGGER_LEVEL, "propagate": True},
#     },
# }


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "api.rest_auth.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
        # "rest_framework.permissions.IsAdminUser",
    ],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

ICON_SRC = os.path.join(BASE_DIR, "static", "favorites_icon.png")
SITE_NAME = "Vryhof.NET"  # Optional if you are using the Sites framework, and have a SITE_ID configured.
TILE_COLOR = "#FFFFFF"
THEME_COLOR = "#000000"

PDL_KEY = "b63861db1bfed5591be4480bf64cd73d743fc981844d8064a5b5fa72dcfa4d83"

SUBSONIC_URL = os.environ.get("SUBSONIC_URL")
SUBSONIC_USER = os.environ.get("SUBSONIC_USER")
SUBSONIC_PASSWORD = os.environ.get("SUBSONIC_PASSWORD")
