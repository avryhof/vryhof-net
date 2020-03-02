from django.conf.urls import url
from django.urls import path

from .views import BlogCategoryView, BlogHomeView, BlogPostView

urlpatterns = [
    url(r"post/(?P<post_slug>[a-z0-9_\-]+)/", BlogPostView.as_view(), name="blog_post"),
    url(r"category/(?P<category_slug>[a-z0-9_\-]+)/", BlogCategoryView.as_view(), name="blog_category"),
    path("", BlogHomeView.as_view(), name="blog_home"),
]
