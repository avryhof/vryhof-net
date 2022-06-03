from django.urls import path

from .views import BlogCategoryView, BlogHomeView, BlogPostView

urlpatterns = [
    path("post/<str:post_slug>/", BlogPostView.as_view(), name="blog_post"),
    path("category/<str:category_slug>/", BlogCategoryView.as_view(), name="blog_category"),
    path("", BlogHomeView.as_view(), name="blog_home"),
]
