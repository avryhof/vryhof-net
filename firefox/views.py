# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from utilities.debugging import get_client_ip, get_ua_string

from firefox.forms import SearchForm
from firefox.models import NewsItem


class FirefoxHomeView(TemplateView):
    extra_css = ["css/ff-style.css"]
    extra_javascript = []

    template_name = "firefox-start.html"
    name = "Firefox Start page"

    request = None

    def get_context_data(self, **kwargs):
        context = super(FirefoxHomeView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        context["form"] = SearchForm()

        yesterday = make_aware(datetime.datetime.now()) - datetime.timedelta(days=1)
        context["news"] = NewsItem.objects.filter(date__gte=yesterday)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        form = SearchForm(request.POST)
        news_items = []

        if form.is_valid():
            terms = form.cleaned_data.get("search")
            news_items = NewsItem.objects.annotate(search=SearchVector("title", "abstract", "content")).filter(
                search=terms
            )
        else:
            yesterday = make_aware(datetime.datetime.now() - datetime.timedelta(days=1))
            news_items = NewsItem.objects.filter(date__gte=yesterday)

        context["news"] = news_items
        context["form"] = form

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(FirefoxHomeView, self).dispatch(*args, **kwargs)


class SearchView(TemplateView):
    extra_css = ["css/ff-style.css"]
    extra_javascript = ["js/search.min.js"]

    template_name = "search-page.html"
    name = "Search"

    request = None

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        context["form"] = SearchForm()

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SearchView, self).dispatch(*args, **kwargs)


class SignatureView(TemplateView):
    extra_css = ["css/ff-style.css"]
    extra_javascript = []

    template_name = "email-signature.html"
    name = "Email Signature"

    request = None

    def get_context_data(self, **kwargs):
        context = super(SignatureView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(SignatureView, self).dispatch(*args, **kwargs)


def my_ip_address(request):
    client_ip = get_client_ip(request)
    ua_string = get_ua_string(request)

    if request.user.is_authenticated:
        log_exception(
            request, None, message=f"IP Address for {request.user.username} ({request.user.email}): {client_ip}"
        )

    return HttpResponse(f"{client_ip}\n{ua_string}")
