from django.urls import path

from .views import *

urlpatterns = [
    path("login/", sign_in, name="login"),
    path("signout/", sign_out, name="signout"),
    path("callback", callback, name="callback"),
    path("photo/", get_photo, name="photo"),
    path("photo/<int:width>/<int:height>/", get_photo, name="photo_sized")
]
