from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView


class IPAddressView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = "kid_sites.html"
    name = "Kid Sites"

    request = None

    def get_context_data(self, **kwargs):
        context = super(IPAddressView, self).get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        print(request)

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super(IPAddressView, self).dispatch(*args, **kwargs)