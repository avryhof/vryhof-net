import bleach
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from blog.models import BlogCategory, BlogPost
from content.helpers import get_page_context
from utilities.utility_functions import is_empty


class BlogHomeView(TemplateView):
    template_name = "blog/page.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super(BlogHomeView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["extra_css"] = ["css/blog.css"]
        context["extra_javascript"] = []

        context = get_page_context("blog_home", context)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(BlogHomeView, self).dispatch(*args, **kwargs)


class BlogCategoryView(TemplateView):
    template_name = "blog/category.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super(BlogCategoryView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["extra_css"] = ["css/blog.css"]
        context["extra_javascript"] = []

        context = get_page_context("blog_category", context)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        category_slug = kwargs.get("category_slug")

        if isinstance(category_slug, str):
            category_slug = bleach.clean(category_slug)

            try:
                category = BlogCategory.objects.get(slug=category_slug)

            except BlogCategory.DoesNotExist:
                return redirect("blog_home")

            else:
                context["category"] = category

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(BlogCategoryView, self).dispatch(*args, **kwargs)


class BlogPostView(TemplateView):
    template_name = "blog/single.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super(BlogPostView, self).get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["extra_css"] = ["css/blog.css"]
        context["extra_javascript"] = []

        context = get_page_context("blog_post", context)

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()

        post_slug = kwargs.get("post_slug")

        if isinstance(post_slug, str):
            post_slug = bleach.clean(post_slug)

            try:
                post = BlogPost.objects.get(slug=post_slug)

            except BlogPost.DoesNotExist:
                return redirect("blog_home")

            else:
                context["post"] = post
                context['category'] = post.category

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(BlogPostView, self).dispatch(*args, **kwargs)
