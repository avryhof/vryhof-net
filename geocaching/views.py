from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from geocaching.constants import GPX_GEOCACHES, GPX_WAYPOINTS
from geocaching.models import Point


class ShowCachesView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = "caches.html"
    name = "GeoCaches"

    request = None

    def get_context_data(self, **kwargs):
        context = super(ShowCachesView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        context['caches'] = Point.objects.filter(point_type=GPX_GEOCACHES)

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(ShowCachesView, self).dispatch(*args, **kwargs)


class ShowCacheView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = "cache.html"
    name = "GeoCaches"

    request = None

    def get_context_data(self, **kwargs):
        context = super(ShowCacheView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        name = kwargs.get('name')

        cache = Point.objects.get(name=name)
        waypoints = Point.objects.filter(point_type=GPX_WAYPOINTS, name__endswith=cache.name.replace('GC', ''))

        self.name = cache.urlname
        context['page_title'] = '%s - %s' % (cache.name, cache.urlname)

        context['cache'] = cache
        context['waypoints'] = waypoints

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(ShowCacheView, self).dispatch(*args, **kwargs)
