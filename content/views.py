from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from content.helpers import get_page_context


class HomeView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = "home.html"
    name = "Home"

    request = None

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        context = get_page_context("home", context)

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(HomeView, self).dispatch(*args, **kwargs)


class PageView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = "home.html"
    name = "Home"

    page_name = None
    request = None

    def get_context_data(self, **kwargs):
        context = super(PageView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        context = get_page_context(self.page_name, context)

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()
        self.page_name = kwargs.get("page_name")

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(PageView, self).dispatch(*args, **kwargs)
