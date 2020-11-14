"""vryhof URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    # path("vryhof-admin/multifactor/", include("multifactor.urls")),
    path("vryhof-admin/", admin.site.urls),
    path("alexa/", include("alexa.urls")),
    path("subsonic/", include("subsonic.urls")),
    path("assistant/", include("assistant.urls")),
    # path("api/mail/", include("mail.api_urls")),
    path("api/rest/", include("api.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("blog/", include("blog.urls")),
    path("", include("firefox.urls")),
    path("weather/", include("weather.urls")),
    path("geocaching/", include("geocaching.urls")),
    path("kids/", include("kids.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG:
    urlpatterns = (
        [re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT, "show_indexes": True})]
        + staticfiles_urlpatterns()
        + urlpatterns
    )
