from django.urls import path

from content.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
]