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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.views.static import serve

urlpatterns = [
    url(r"^vryhof-admin/", admin.site.urls),
    url(r"^alexa/", include("alexa.urls")),
    url(r"^assistant/", include("assistant.urls")),
    # url(r"^api/mail/", include("mail.api_urls")),
    url(r"^api/rest/", include("api.urls")),
    url(r"^api-auth/", include("rest_framework.urls")),
    url(r"^blog/", include("blog.urls")),
    url(r"", include("firefox.urls")),
    url(r"^weather/", include("weather.urls")),
    url(r"^geocaching/", include("geocaching.urls")),
    url(r"^ckeditor/", include("ckeditor_uploader.urls")),
]

if settings.DEBUG:
    urlpatterns = (
        [url(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT, "show_indexes": True})]
        + staticfiles_urlpatterns()
        + urlpatterns
    )
