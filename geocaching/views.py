from django.db.models import Q, QuerySet
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from geocaching.constants import GPX_GEOCACHES, GPX_WAYPOINTS
from geocaching.forms import CacheSearchForm
from geocaching.models import Point
from geocaching.utility_functions import get_points_in_radius


class ShowCachesView(TemplateView):
    extra_css = []
    extra_javascript = ['js/caches.js']

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

        context['search_form'] = CacheSearchForm
        context['caches'] = Point.objects.filter(point_type=GPX_GEOCACHES)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        form = CacheSearchForm(request.POST)
        caches = []

        if form.is_valid():
            terms = form.cleaned_data.get('terms')
            latitude = form.cleaned_data.get('latitude')
            longitude = form.cleaned_data.get('longitude')

            if latitude and longitude:
                caches = []
                sorted_caches = get_points_in_radius(latitude, longitude)

                for sorted_cache in sorted_caches:
                    if sorted_cache.point_type == GPX_GEOCACHES and (
                            terms.lower() in sorted_cache.name.lower() or terms.lower() in sorted_cache.urlname.lower()
                            or terms.lower() in sorted_cache.long_description.lower()):
                        caches.append(sorted_cache)

            else:
                caches = Point.objects.filter(point_type=GPX_GEOCACHES).filter(
                    Q(name__icontains=terms) | Q(urlname__icontains=terms) | Q(long_description__icontains=terms))

        context['search_form'] = form
        context['caches'] = caches

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(ShowCachesView, self).dispatch(*args, **kwargs)


class ShowCacheView(TemplateView):
    extra_css = ['css/cache.css']
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
