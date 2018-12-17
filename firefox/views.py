# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from firefox.utilities import get_feeds


class FirefoxHomeView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = 'firefox-start.html'
    name = 'Firefox Start page'

    request = None

    def get_context_data(self, **kwargs):
        context = super(FirefoxHomeView, self).get_context_data(**kwargs)
        context['page_title'] = self.name
        context['extra_css'] = self.extra_css
        context['extra_javascript'] = self.extra_javascript
        context['request'] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        context['news'] = get_feeds()

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):

        return super(FirefoxHomeView, self).dispatch(*args, **kwargs)
