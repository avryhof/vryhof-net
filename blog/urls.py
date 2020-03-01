from django.conf.urls import url

from .views import BlogCategoryView, BlogHomeView, BlogPostView

urlpatterns = [
    url(r'post/(?P<post_slug>[a-z0-9_\-]+)/', BlogPostView.as_view(), name='blog_post'),
    url(r'category/(?P<category_slug>[a-z0-9_\-]+)/', BlogCategoryView.as_view(), name='blog_category'),
    url(r'^$', BlogHomeView.as_view(), name='blog_home')
]
