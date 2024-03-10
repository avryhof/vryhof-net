from django.urls import path
from django.views.generic import RedirectView

from .views import *

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("login/token/<str:token>/", LoginTokenView.as_view(), name="login-token"),
    path("login/token/", LoginTokenView.as_view(), name="login-token"),
    path("signout/", sign_out, name="logout"),
    path("sign-out/", RedirectView.as_view(pattern_name="logout"), name="signout"),
    path("profile/edit/", AccountProfileEditView.as_view(), name="account-profile-edit"),
    path("profile/", AccountProfileView.as_view(), name="account-profile"),
]
