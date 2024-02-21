from django.urls import path

from amos.views import CVView, CVPageView

urlpatterns = [
    path("page/<str:page_slug>/", CVPageView.as_view(), name="cv-page"),
    path("", CVView.as_view(), name="cv"),
]
