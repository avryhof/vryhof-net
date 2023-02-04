from django.urls import path

from me.views import MeView, EditMeView

urlpatterns = [
    path("", MeView.as_view(), name="member-home"),
    path("edit/", EditMeView.as_view(), name="member-edit"),
]
