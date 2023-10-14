from django.urls import path

from content.views import HomeView, PageView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("page/<str:page_name>/", PageView.as_view(), name="page"),
]