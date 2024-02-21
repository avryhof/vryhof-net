from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView

from utilities.model_helper import load_model


class CVView(TemplateView):
    extra_css = []
    extra_javascript = []

    template_name = "card-home.html"
    name = "Amos Vryhof"

    request = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        page_model = load_model("amos.CVPage")
        context["cv_pages"] = page_model.objects.filter(enabled=True).order_by("order")

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()

        page_model = load_model("amos.CVPage")
        try:
            page = page_model.objects.get(home=True)
        except page_model.DoesNotExist:
            raise Http404("Page not found.")
        else:
            context["page"] = page
            context["page_title"] = page.page_title
            self.template_name = page.template

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CVPageView(TemplateView):
    extra_css = ["css/home.css"]
    extra_javascript = []

    template_name = "card-page.html"
    name = "Home"

    page_name = None
    request = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.name
        context["extra_css"] = self.extra_css
        context["extra_javascript"] = self.extra_javascript
        context["request"] = self.request

        page_model = load_model("amos.CVPage")
        context["cv_pages"] = page_model.objects.filter(enabled=True).order_by("order")

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = self.get_context_data()
        self.page_name = kwargs.get("page_slug")

        page_model = load_model("amos.CVPage")
        try:
            page = page_model.objects.get(url_name=self.page_name)
        except page_model.DoesNotExist:
            raise Http404("Page not found.")
        else:
            context["page"] = page
            context["page_title"] = page.page_title
            self.template_name = page.template

        return render(request, self.template_name, context)

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
